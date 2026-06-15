# strategies/ma_crossover.py
from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class MACrossoverStrategy(BaseStrategy):
    def __init__(self, symbol="EURUSD", fast_period=20, slow_period=50):
        super().__init__(symbol)
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def calculate_indicators(self, data):
        """Calculate moving averages"""
        data['ma_fast'] = data['close'].rolling(window=self.fast_period).mean()
        data['ma_slow'] = data['close'].rolling(window=self.slow_period).mean()
        return data
    
    def generate_signals(self, data):
        """Generate moving average crossover signals"""
        data = self.calculate_indicators(data)
        
        signals = []
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Bullish crossover
        if (previous['ma_fast'] <= previous['ma_slow'] and 
            latest['ma_fast'] > latest['ma_slow']):
            signals.append({
                'type': 'BUY',
                'symbol': self.symbol,
                'entry_price': latest['close'],
                'strategy': 'MA_CROSSOVER'
            })
        
        # Bearish crossover
        elif (previous['ma_fast'] >= previous['ma_slow'] and 
              latest['ma_fast'] < latest['ma_slow']):
            signals.append({
                'type': 'SELL',
                'symbol': self.symbol,
                'entry_price': latest['close'],
                'strategy': 'MA_CROSSOVER'
            })
        
        return signals
    
    def validate_signal(self, signal):
        """Validate signal with additional filters"""
        # Add your validation logic here
        return True
    
    def check_signals(self):
        """Main method to check for signals"""
        # This would connect to real data in production
        # For now, return simulated signal
        return []