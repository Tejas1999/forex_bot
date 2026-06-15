# strategies/breakout_strategy.py
from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class BreakoutStrategy(BaseStrategy):
    def __init__(self, symbol="EURUSD", period=20, multiplier=2.0):
        super().__init__(symbol)
        self.period = period
        self.multiplier = multiplier
    
    def calculate_bollinger_bands(self, data):
        """Calculate Bollinger Bands"""
        data['ma'] = data['close'].rolling(window=self.period).mean()
        data['std'] = data['close'].rolling(window=self.period).std()
        data['upper_band'] = data['ma'] + (data['std'] * self.multiplier)
        data['lower_band'] = data['ma'] - (data['std'] * self.multiplier)
        return data
    
    def generate_signals(self, data):
        """Generate breakout signals"""
        data = self.calculate_bollinger_bands(data)
        
        signals = []
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Breakout above upper band
        if previous['close'] <= previous['upper_band'] and latest['close'] > latest['upper_band']:
            signals.append({
                'type': 'BUY',
                'symbol': self.symbol,
                'entry_price': latest['close'],
                'indicator': 'BREAKOUT_UPPER',
                'band_value': latest['upper_band']
            })
        
        # Breakdown below lower band
        elif previous['close'] >= previous['lower_band'] and latest['close'] < latest['lower_band']:
            signals.append({
                'type': 'SELL',
                'symbol': self.symbol,
                'entry_price': latest['close'],
                'indicator': 'BREAKOUT_LOWER',
                'band_value': latest['lower_band']
            })
        
        return signals
    
    def validate_signal(self, signal):
        """Validate breakout signal"""
        # Add volume confirmation or other filters
        return True