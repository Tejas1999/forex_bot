# data/data_handler.py
import pandas as pd
import numpy as np
from datetime import datetime
import logging

class DataHandler:
    def __init__(self):
        self.data_cache = {}
    
    def clean_data(self, df):
        """Clean and validate market data"""
        try:
            # Remove duplicates
            df = df.drop_duplicates(subset=['time'])
            
            # Sort by time
            df = df.sort_values('time')
            
            # Handle missing values
            df = df.fillna(method='ffill').fillna(method='bfill')
            
            # Validate price data
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove invalid rows
            df = df.dropna()
            
            # Validate price relationships
            df = df[(df['high'] >= df['low']) & 
                   (df['high'] >= df['open']) & 
                   (df['high'] >= df['close']) &
                   (df['low'] <= df['open']) & 
                   (df['low'] <= df['close'])]
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            logging.error(f"Error cleaning data: {str(e)}")
            return df
    
    def resample_data(self, df, timeframe='1H'):
        """Resample data to different timeframe"""
        try:
            df_copy = df.copy()
            df_copy.set_index('time', inplace=True)
            
            resampled = df_copy.resample(timeframe).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            resampled.reset_index(inplace=True)
            return resampled
            
        except Exception as e:
            logging.error(f"Error resampling data: {str(e)}")
            return df
    
    def add_technical_indicators(self, df):
        """Add technical indicators to data"""
        from indicators.technical_indicators import TechnicalIndicators
        return TechnicalIndicators.add_all_indicators(df)