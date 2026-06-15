# broker/account_manager.py
import MetaTrader5 as mt5
import logging

class AccountManager:
    def __init__(self):
        self.account_info = None
    
    def get_account_info(self):
        """Get account information"""
        try:
            info = mt5.account_info()
            if info is None:
                logging.error("Failed to get account info")
                return None
            
            self.account_info = {
                'balance': info.balance,
                'equity': info.equity,
                'margin': info.margin,
                'free_margin': info.margin_free,
                'margin_level': info.margin_level,
                'currency': info.currency,
                'leverage': info.leverage,
                'login': info.login
            }
            
            return self.account_info
            
        except Exception as e:
            logging.error(f"Error getting account info: {str(e)}")
            return None
    
    def get_account_balance(self):
        """Get account balance"""
        info = self.get_account_info()
        return info['balance'] if info else 0
    
    def get_free_margin(self):
        """Get free margin"""
        info = self.get_account_info()
        return info['free_margin'] if info else 0
    
    def get_margin_level(self):
        """Get margin level"""
        info = self.get_account_info()
        return info['margin_level'] if info else 0
    
    def is_margin_call(self):
        """Check if margin call level is reached"""
        margin_level = self.get_margin_level()
        return margin_level < 100 if margin_level > 0 else False
    
    def get_positions(self):
        """Get all open positions"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            return list(positions)
            
        except Exception as e:
            logging.error(f"Error getting positions: {str(e)}")
            return []
    
    def get_position_count(self):
        """Get number of open positions"""
        positions = self.get_positions()
        return len(positions)