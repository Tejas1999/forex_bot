# risk/risk_manager.py
from config.settings import Config
import MetaTrader5 as mt5
import logging

class RiskManager:
    def __init__(self):
        self.max_risk_percent = Config.MAX_RISK_PERCENT
        self.max_positions = Config.MAX_POSITIONS
        self.stop_loss_pips = Config.STOP_LOSS_PIPS
    
    def calculate_position_size(self, symbol, entry_price):
        """Calculate position size based on risk management"""
        try:
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                return Config.LOT_SIZE
            
            account_balance = account_info.balance
            
            # Calculate risk amount
            risk_amount = account_balance * (self.max_risk_percent / 100)
            
            # Get symbol info for pip value
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return Config.LOT_SIZE
            
            # Calculate position size
            pip_value = symbol_info.trade_tick_value * 10  # Approximate
            position_size = risk_amount / (self.stop_loss_pips * pip_value)
            
            # Convert to standard lot sizes
            lot_sizes = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
            lot_size = min(lot_sizes, key=lambda x: abs(x - (position_size / 100000)))
            
            # Ensure minimum lot size
            lot_size = max(lot_size, 0.01)
            
            logging.info(f"📊 Position size calculated: {lot_size} lots for {symbol}")
            return lot_size
            
        except Exception as e:
            logging.error(f"Error calculating position size: {str(e)}")
            return Config.LOT_SIZE
    
    def check_risk_limits(self):
        """Check if we're within risk limits"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return True
            
            if len(positions) >= self.max_positions:
                logging.warning(f"⚠️ Max positions reached: {len(positions)}")
                return False
            
            return True
        except Exception as e:
            logging.error(f"Error checking risk limits: {str(e)}")
            return True