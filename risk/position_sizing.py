# risk/position_sizing.py
import MetaTrader5 as mt5
from config.settings import Config
from config.symbols import SYMBOLS_CONFIG
from utils.helpers import get_pip_size, get_symbol_type
import logging

class PositionSizing:
    @staticmethod
    def calculate_fixed_lot_size(symbol, fixed_lot=0.01):
        """Calculate fixed lot size"""
        symbol_config = SYMBOLS_CONFIG.get(symbol, {})
        return symbol_config.get('lot_size', fixed_lot)
    
    @staticmethod
    def calculate_percentage_risk(account_balance, risk_percent=2.0):
        """Calculate dollar amount risked"""
        return account_balance * (risk_percent / 100)
    
    @staticmethod
    def calculate_position_size_by_risk(symbol, entry_price, stop_loss_price, risk_amount):
        """Calculate position size based on risk amount and stop loss"""
        try:
            # Get symbol information
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                symbol_config = SYMBOLS_CONFIG.get(symbol, {})
                return symbol_config.get('lot_size', Config.LOT_SIZE)
            
            # Calculate pip value and stop loss distance
            pip_size = get_pip_size(symbol)
            sl_distance = abs(entry_price - stop_loss_price) / pip_size
            pip_value = symbol_info.trade_tick_value
            
            # For crypto and commodities, use contract size
            symbol_config = SYMBOLS_CONFIG.get(symbol, {})
            if 'contract_size' in symbol_config:
                contract_size = symbol_config['contract_size']
                pip_value = pip_value * contract_size
            
            # Calculate position size
            if sl_distance > 0 and pip_value > 0:
                position_size = risk_amount / (sl_distance * pip_value)
                
                # Convert to standard lot sizes based on symbol type
                symbol_type = get_symbol_type(symbol)
                if symbol_type == 'crypto':
                    lot_sizes = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
                elif symbol_type == 'commodity':
                    lot_sizes = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
                else:  # forex
                    lot_sizes = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
                
                lot_size = min(lot_sizes, key=lambda x: abs(x - position_size))
                
                # Ensure within symbol limits
                lot_size = max(lot_size, symbol_config.get('min_volume', symbol_info.volume_min))
                lot_size = min(lot_size, symbol_config.get('max_volume', symbol_info.volume_max))
                
                return round(lot_size, 2)
            
            return Config.LOT_SIZE
            
        except Exception as e:
            logging.error(f"Error calculating position size: {str(e)}")
            return Config.LOT_SIZE
    
    @staticmethod
    def calculate_kelly_criterion(win_rate, win_loss_ratio):
        """Calculate optimal position size using Kelly Criterion"""
        if win_loss_ratio <= 0:
            return 0
        
        kelly = win_rate - ((1 - win_rate) / win_loss_ratio)
        return max(0, min(kelly, 0.25))  # Cap at 25% for safety