import time
import os
import MetaTrader5 as mt5
import pandas as pd
from flask import Flask
from flask_socketio import SocketIO
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque
from functools import wraps

from config.settings import Config
from broker.mt5_connector import MT5Connector
from strategies.ma_crossover import MACrossoverStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.breakout_strategy import BreakoutStrategy
from strategies.scalping_strategy import ScalpingStrategy
from risk.risk_manager import RiskManager
from utils.logger import setup_logger
from web.routes.dashboard_routes import dashboard_bp, set_globals

app = Flask(__name__, 
           template_folder='web/templates',
           static_folder='web/static',
           static_url_path='/static')
app.config['SECRET_KEY'] = 'forex-bot-secret-key'
app.register_blueprint(dashboard_bp)
socketio = SocketIO(app, cors_allowed_origins="*")

bot_status = {
    'running': False,
    'status': 'stop',
    'balance': 0.00,
    'equity': 0.00,
    'free_margin': 0.00,
    'positions': [],
    'logs': [],
    'symbols': Config.SYMBOLS,
    'last_signals': {}
}
set_globals(None, None, bot_status, socketio)

def log_exceptions(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in {func.__name__}: {str(e)}")
            return None if func.__name__.startswith('get_') else False
    return wrapper

class TradingBot:
    def __init__(self):
        self.logger = setup_logger()
        self.connector = MT5Connector()
        self.risk_manager = RiskManager()
        self.running = False
        self.processed_signals = deque(maxlen=200)
        self.strategies = {
            symbol: {
                'ma': MACrossoverStrategy(symbol),
                'rsi': RSIStrategy(symbol),
                'breakout': BreakoutStrategy(symbol),
                'scalping': ScalpingStrategy(symbol)
            } for symbol in Config.SYMBOLS
        }

    def add_strategy(self, strategy_obj):
        """Register a new strategy instance for its symbol.

        strategy_obj must have a `symbol` attribute. The strategy will be
        stored under a key derived from its class name so it can be called
        by the main loop without further changes.
        """
        symbol = getattr(strategy_obj, 'symbol', None)
        if not symbol:
            return False
        key = strategy_obj.__class__.__name__.lower()
        if symbol not in self.strategies:
            self.strategies[symbol] = {}
        self.strategies[symbol][key] = strategy_obj
        self.logger.info(f"Strategy {strategy_obj.__class__.__name__} added for {symbol}")
        return True

    @log_exceptions
    def initialize(self) -> bool:
        if not self.connector.initialize():
            self.logger.error("Failed to initialize MT5 connection")
            return False
        self.logger.info("MT5 Connection Established")
        return True

    @log_exceptions
    def get_market_data(self, symbol: str, timeframe=mt5.TIMEFRAME_M1, bars: int=100) -> Optional[pd.DataFrame]:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        if rates is not None:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
        return None

    @log_exceptions
    def get_open_positions_for_symbol(self, symbol: str) -> List[Any]:
        positions = mt5.positions_get(symbol=symbol)
        return positions if positions is not None else []

    def validate_signal(self, signal: Dict[str, Any], symbol: str) -> bool:
        try:
            if self.get_open_positions_for_symbol(symbol):
                self.logger.info(f"Skipping {symbol} - Position already open")
                return False
            signal_key = f"{symbol}_{signal.get('type', '')}_{signal.get('indicator', '')}_{int(time.time() / 60)}"
            if signal_key in self.processed_signals:
                return False
            symbol_info = mt5.symbol_info(signal['symbol'])
            # `symbol_info.trade_mode` is an integer constant, not a callable.
            # Compare the attribute value instead of attempting to call it.
            if symbol_info is None or getattr(symbol_info, 'trade_mode', None) != mt5.SYMBOL_TRADE_MODE_FULL:
                self.logger.warning(f"Symbol {signal['symbol']} is not fully tradable")
                return False
            spread_limit = getattr(symbol_info, 'spread_limit', 5)
            if hasattr(symbol_info, 'spread') and symbol_info.spread > spread_limit:
                self.logger.warning(f"High spread for {signal['symbol']}: {symbol_info.spread}")
                return False
            account_info = mt5.account_info()
            if account_info and account_info.margin_level < 100:
                self.logger.warning("Low margin level, skipping trade")
                return False
            all_positions = mt5.positions_get()
            if all_positions is not None and len(all_positions) >= Config.MAX_POSITIONS:
                self.logger.warning("Maximum positions reached")
                return False
            self.processed_signals.append(signal_key)
            return True
        except Exception as e:
            self.logger.error(f"Error validating signal for {symbol}: {str(e)}")
            return False

    @log_exceptions
    def get_account_info(self) -> Dict[str, float]:
        account_info = mt5.account_info()
        if account_info:
            return {
                'balance': round(account_info.balance, 2),
                'equity': round(account_info.equity, 2),
                'free_margin': round(account_info.margin_free, 2),
                'margin_level': round(account_info.margin_level, 2)
            }
        return {k: 0.00 for k in ['balance', 'equity', 'free_margin', 'margin_level']}

    @log_exceptions
    def get_positions(self) -> List[Dict[str, Any]]:
        positions = mt5.positions_get()
        if positions:
            return [{
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == 0 else 'SELL',
                'lots': pos.volume,
                'price': round(pos.price_open, 5),
                'sl': round(pos.sl, 5) if pos.sl > 0 else 0,
                'tp': round(pos.tp, 5) if pos.tp > 0 else 0,
                'pnl': round(pos.profit, 2)
            } for pos in positions]
        return []

    def update_dashboard_data(self):
        account_info = self.get_account_info()
        positions = self.get_positions()
        bot_status.update({
            'balance': account_info['balance'],
            'equity': account_info['equity'],
            'free_margin': account_info['free_margin'],
            'margin_level': account_info['margin_level'],
            'positions': positions
        })
        try:
            socketio.emit('status_update', bot_status)
        except Exception as e:
            self.logger.error(f"Error emitting socketio update: {str(e)}")

    def execute_trading_cycle(self) -> bool:
        try:
            signals_found = []
            for symbol in Config.SYMBOLS:
                if self.get_open_positions_for_symbol(symbol):
                    continue
                data = self.get_market_data(symbol, bars=200)
                if data is None or len(data) < 50:
                    continue
                symbol_signals = []
                for strat_name in ['ma', 'rsi', 'breakout', 'scalping']:
                    try:
                        strat = self.strategies[symbol][strat_name]
                        symbol_signals.extend(strat.generate_signals(data))
                    except Exception as e:
                        self.logger.error(f"Error in {strat_name.upper()} strategy for {symbol}: {str(e)}")
                for signal in symbol_signals:
                    signal['symbol'] = symbol
                    if self.validate_signal(signal, symbol):
                        position_size = self.risk_manager.calculate_position_size(symbol, signal['entry_price'])
                        signal['position_size'] = position_size
                        result = self.connector.place_order(signal, position_size)
                        if result:
                            self.logger.info(f"✅ ORDER PLACED: {signal['type']} {symbol} at {signal['entry_price']:.5f}, Size: {position_size}")
                            signals_found.append({
                                'symbol': symbol,
                                'type': signal['type'],
                                'price': signal['entry_price'],
                                'size': position_size,
                                'indicator': signal.get('indicator', 'UNKNOWN'),
                                'time': datetime.now().strftime('%H:%M:%S')
                            })
                            break
                        else:
                            self.logger.error(f"❌ FAILED to place order for {symbol}")
            if signals_found:
                for signal in signals_found:
                    log_message = f"🎯 Signal Executed: {signal['type']} {signal['symbol']} @ {signal['price']:.5f} ({signal['indicator']})"
                    bot_status['logs'].append({'time': signal['time'], 'message': log_message})
                    self.logger.info(log_message)
            return True
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {str(e)}")
            return False

    def run(self) -> bool:
        if not self.initialize():
            return False
        self.running = True
        bot_status['running'] = True
        bot_status['status'] = 'start'
        self.logger.info("Starting Trading Bot")
        try:
            socketio.emit('status_update', bot_status)
        except Exception as e:
            self.logger.error(f"Error emitting initial socketio update: {str(e)}")
        try:
            cycle_count = 0
            while self.running:
                cycle_count += 1
                self.update_dashboard_data()
                self.execute_trading_cycle()
                self.logger.info(f"Trading cycle {cycle_count} completed - Balance: ${bot_status['balance']}, Equity: ${bot_status['equity']}")
                time.sleep(Config.CHECK_INTERVAL)
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
        return True

    def stop(self):
        self.running = False
        bot_status['running'] = False
        bot_status['status'] = 'stop'
        self.logger.info("Trading bot stopped")
        try:
            socketio.emit('status_update', bot_status)
        except Exception as e:
            self.logger.error(f"Error emitting stop socketio update: {str(e)}")

@socketio.on('connect')
def handle_connect():
    setup_logger().info('Client connected')
    socketio.emit('status_update', bot_status)

@socketio.on('disconnect')
def handle_disconnect():
    setup_logger().info('Client disconnected')

def ensure_directories():
    for path in [
        'web/templates',
        'web/static/css',
        'web/static/js',
        'web/routes'
    ]:
        os.makedirs(path, exist_ok=True)

def main():
    ensure_directories()
    print("🚀 Starting Forex Trading Bot with Web Dashboard")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⚠️  Make sure MT5 is running and logged into your DEMO account")
    bot_status['symbols'] = Config.SYMBOLS
    set_globals(None, None, bot_status, socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()
