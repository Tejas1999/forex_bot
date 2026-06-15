# strategies/rsi_strategy.py
from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class RSIStrategy(BaseStrategy):
    def __init__(self, symbol="EURUSD", period=14, overbought=70, oversold=30):
        super().__init__(symbol)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate_rsi(self, data):
        """Calculate RSI indicator"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        return data
    
    def generate_signals(self, data):
        """Generate RSI signals"""
        data = self.calculate_rsi(data)
        
        signals = []
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Oversold condition - potential buy
        if previous['rsi'] > self.oversold and latest['rsi'] <= self.oversold:
            signals.append({
                'type': 'BUY',
                'symbol': self.symbol,
                'entry_price': latest['close'],
                'indicator': 'RSI_OVERSOLD',
                'rsi_value': latest['rsi']
            })
        
        # Overbought condition - potential sell
        elif previous['rsi'] < self.overbought and latest['rsi'] >= self.overbought:
            signals.append({
                'type': 'SELL',
                'symbol': self.symbol,
                'entry_price': latest['close'],
                'indicator': 'RSI_OVERBOUGHT',
                'rsi_value': latest['rsi']
            })
        
        return signals
    
    def validate_signal(self, signal):
        """Validate RSI signal"""
        # Add additional validation logic
        rsi_value = signal.get('rsi_value', 50)
        
        # Ensure extreme RSI values for stronger signals
        if signal['type'] == 'BUY' and rsi_value <= 25:
            return True
        elif signal['type'] == 'SELL' and rsi_value >= 75:
            return True
        
        return False