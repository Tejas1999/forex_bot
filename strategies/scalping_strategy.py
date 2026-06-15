# strategies/scalping_strategy.py
from .base_strategy import BaseStrategy
import pandas as pd
import numpy as np

class ScalpingStrategy(BaseStrategy):
    def __init__(self, symbol="EURUSD", fast_period=5, slow_period=10):
        super().__init__(symbol)
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def calculate_indicators(self, data):
        """Calculate scalping indicators"""
        data['ema_fast'] = data['close'].ewm(span=self.fast_period).mean()
        data['ema_slow'] = data['close'].ewm(span=self.slow_period).mean()
        
        # Price action indicators
        data['range'] = data['high'] - data['low']
        data['avg_range'] = data['range'].rolling(window=14).mean()
        
        return data
    
    def generate_signals(self, data):
        """Generate scalping signals"""
        data = self.calculate_indicators(data)
        
        signals = []
        latest = data.iloc[-1]
        previous = data.iloc[-2]
        
        # Fast EMA crossing above slow EMA with increasing volume
        if (previous['ema_fast'] <= previous['ema_slow'] and 
            latest['ema_fast'] > latest['ema_slow']):
            signals.append({
                'type': 'BUY',
                'symbol': self.symbol,
                'entry_price': latest['close'],
                'indicator': 'SCALPING_BULLISH',
                'ema_fast': latest['ema_fast'],
                'ema_slow': latest['ema_slow']
            })
        
        # Fast EMA crossing below slow EMA
        elif (previous['ema_fast'] >= previous['ema_slow'] and 
              latest['ema_fast'] < latest['ema_slow']):
            signals.append({
                'type': 'SELL',
                'symbol': self.symbol,
                'entry_price': latest['close'],
                'indicator': 'SCALPING_BEARISH',
                'ema_fast': latest['ema_fast'],
                'ema_slow': latest['ema_slow']
            })
        
        return signals
    
    def validate_signal(self, signal):
        """Validate scalping signal"""
        # Add time-based filters (avoid news times)
        # Add spread filters
        return True