# broker/mt5_connector.py
import MetaTrader5 as mt5
from config.settings import Config
import logging

class MT5Connector:
    def __init__(self):
        self.connected = False
    
    def initialize(self):
        """Initialize MT5 connection"""
        try:
            if not mt5.initialize(Config.MT5_PATH):
                logging.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            # Test connection
            account_info = mt5.account_info()
            if account_info is None:
                logging.error("Failed to get account info")
                return False
            
            logging.info(f"Connected to account: {account_info.login}")
            self.connected = True
            return True
            
        except Exception as e:
            logging.error(f"MT5 connection error: {str(e)}")
            return False
    
    def get_market_data(self, symbol, timeframe=mt5.TIMEFRAME_M1, count=100):
        """Get market data for symbol"""
        if not self.connected:
            return None
        
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None:
                return None
            
            import pandas as pd
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
            
        except Exception as e:
            logging.error(f"Error getting market data: {str(e)}")
            return None
    
    def place_order(self, signal, lot_size):
        """Place order based on signal"""
        if not self.connected:
            return False
        
        try:
            symbol = signal['symbol']
            order_type = signal['type']
            
            # Prepare order request
            if order_type == 'BUY':
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": mt5.symbol_info_tick(symbol).ask,
                    "sl": signal.get('sl', 0),
                    "tp": signal.get('tp', 0),
                    "deviation": 20,
                    "magic": 234000,
                    "comment": f"Bot_{signal['strategy']}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
            else:  # SELL
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": mt5.symbol_info_tick(symbol).bid,
                    "sl": signal.get('sl', 0),
                    "tp": signal.get('tp', 0),
                    "deviation": 20,
                    "magic": 234000,
                    "comment": f"Bot_{signal['strategy']}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
            
            # Send order
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Order failed: {result.retcode}")
                return False
            
            logging.info(f"Order placed: {result.order}")
            return True
            
        except Exception as e:
            logging.error(f"Error placing order: {str(e)}")
            return False
    
    def manage_positions(self):
        """Manage existing positions"""
        if not self.connected:
            return
        
        try:
            positions = mt5.positions_get()
            if positions is None:
                return
            
            for position in positions:
                # Implement trailing stop, position management
                pass
                
        except Exception as e:
            logging.error(f"Error managing positions: {str(e)}")