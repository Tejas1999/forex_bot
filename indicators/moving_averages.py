# indicators/moving_averages.py
import pandas as pd
import numpy as np

class MovingAverages:
    @staticmethod
    def simple_moving_average(data, period):
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def exponential_moving_average(data, period):
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    @staticmethod
    def weighted_moving_average(data, period):
        """Calculate Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        return data.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    
    @staticmethod
    def hull_moving_average(data, period):
        """Calculate Hull Moving Average"""
        half_length = int(period / 2)
        sqrt_length = int(np.sqrt(period))
        
        wma_half = MovingAverages.weighted_moving_average(data, half_length)
        wma_full = MovingAverages.weighted_moving_average(data, period)
        
        hull = (2 * wma_half) - wma_full
        return MovingAverages.weighted_moving_average(hull, sqrt_length)