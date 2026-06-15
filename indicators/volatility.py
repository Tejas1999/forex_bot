# indicators/volatility.py
import pandas as pd
import numpy as np

class VolatilityIndicators:
    @staticmethod
    def average_true_range(high, low, close, period=14):
        """Calculate Average True Range"""
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()
    
    @staticmethod
    def bollinger_bands(data, period=20, multiplier=2):
        """Calculate Bollinger Bands"""
        middle_band = data.rolling(window=period).mean()
        std_dev = data.rolling(window=period).std()
        upper_band = middle_band + (std_dev * multiplier)
        lower_band = middle_band - (std_dev * multiplier)
        return middle_band, upper_band, lower_band
    
    @staticmethod
    def keltner_channels(high, low, close, period=20, multiplier=2):
        """Calculate Keltner Channels"""
        typical_price = (high + low + close) / 3
        middle_line = typical_price.ewm(span=period).mean()
        
        # ATR calculation
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.ewm(span=period).mean()
        
        upper_channel = middle_line + (atr * multiplier)
        lower_channel = middle_line - (atr * multiplier)
        
        return middle_line, upper_channel, lower_channel