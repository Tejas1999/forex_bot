# indicators/technical_indicators.py
import pandas as pd
import numpy as np
import concurrent.futures
from utils.parallel_processor import processor
from .moving_averages import MovingAverages
from .oscillators import Oscillators
from .volatility import VolatilityIndicators
import logging

class TechnicalIndicators:
    @staticmethod
    def add_all_indicators_parallel(df):
        """Add all technical indicators using parallel processing"""
        # Define indicator functions
        indicator_functions = [
            MovingAverages.add_moving_averages,
            Oscillators.add_oscillators,
            VolatilityIndicators.add_volatility_indicators
        ]
        
        # Process indicators in parallel
        results = processor.process_indicators_parallel(df, indicator_functions)
        
        # Merge results
        result_df = df.copy()
        for indicator_data in results.values():
            if indicator_data is not None:
                # Merge new columns
                for col in indicator_data.columns:
                    if col not in result_df.columns:
                        result_df[col] = indicator_data[col]
        
        return result_df

class MovingAveragesParallel:
    @staticmethod
    def calculate_multiple_mas_parallel(data, periods_list):
        """Calculate multiple moving averages in parallel"""
        def calculate_single_ma(period):
            return f"sma_{period}", data.rolling(window=period).mean()
        
        # Process in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(periods_list)) as executor:
            futures = [executor.submit(calculate_single_ma, period) for period in periods_list]
            
            results = {}
            for future in concurrent.futures.as_completed(futures):
                try:
                    col_name, ma_series = future.result()
                    results[col_name] = ma_series
                except Exception as e:
                    logging.error(f"Error calculating MA: {str(e)}")
        
        return results

class OscillatorsParallel:
    @staticmethod
    def calculate_multiple_oscillators_parallel(df):
        """Calculate multiple oscillators in parallel"""
        def rsi_task():
            return Oscillators.add_rsi(df.copy())
        
        def stochastic_task():
            return Oscillators.add_stochastic(df.copy())
        
        def macd_task():
            return Oscillators.add_macd(df.copy())
        
        tasks = [rsi_task, stochastic_task, macd_task]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(task) for task in tasks]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logging.error(f"Error calculating oscillator: {str(e)}")
                    results.append(df.copy())
        
        return results