# risk/money_management.py
from config.settings import Config
import logging

class MoneyManagement:
    def __init__(self):
        self.max_daily_loss = 0.05  # 5% daily loss limit
        self.max_consecutive_losses = 3
        self.consecutive_losses = 0
        self.daily_pnl = 0
        self.max_drawdown = 0.20  # 20% maximum drawdown
    
    def check_daily_limit(self, account_balance, daily_pnl):
        """Check if daily loss limit is reached"""
        daily_loss_percent = abs(daily_pnl) / account_balance
        return daily_loss_percent >= self.max_daily_loss
    
    def check_consecutive_losses(self, trade_result):
        """Check consecutive losses"""
        if trade_result < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        return self.consecutive_losses >= self.max_consecutive_losses
    
    def adjust_position_size(self, base_size, consecutive_losses):
        """Adjust position size based on consecutive losses"""
        if consecutive_losses >= 2:
            return base_size * 0.5  # Reduce by 50%
        elif consecutive_losses >= 1:
            return base_size * 0.75  # Reduce by 25%
        return base_size
    
    def check_drawdown(self, initial_balance, current_balance):
        """Check maximum drawdown"""
        drawdown = (initial_balance - current_balance) / initial_balance
        return drawdown >= self.max_drawdown
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_pnl = 0
        self.consecutive_losses = 0