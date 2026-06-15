# utils/parallel_processor.py
import concurrent.futures
import threading
import multiprocessing as mp
from functools import partial
import logging
from typing import List, Callable, Any
import time

class ParallelProcessor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or min(32, (mp.cpu_count() or 1) + 4)
        self.thread_local = threading.local()
        
    def process_symbols_parallel(self, symbols: List[str], processing_function: Callable, *args, **kwargs) -> dict:
        """
        Process multiple symbols in parallel
        Returns dict with symbol as key and result as value
        """
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(processing_function, symbol, *args, **kwargs): symbol 
                for symbol in symbols
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    results[symbol] = result
                except Exception as e:
                    logging.error(f"Error processing {symbol}: {str(e)}")
                    results[symbol] = None
        
        return results
    
    def process_data_parallel(self, data_chunks: List, processing_function: Callable, *args, **kwargs) -> List:
        """
        Process data chunks in parallel
        """
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(processing_function, chunk, *args, **kwargs) 
                for chunk in data_chunks
            ]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logging.error(f"Error in parallel processing: {str(e)}")
                    results.append(None)
        
        return results
    
    def process_indicators_parallel(self, data, indicator_functions: List[Callable]) -> dict:
        """
        Calculate multiple indicators in parallel
        """
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(indicator_functions)) as executor:
            future_to_indicator = {
                executor.submit(func, data): func.__name__ 
                for func in indicator_functions
            }
            
            for future in concurrent.futures.as_completed(future_to_indicator):
                indicator_name = future_to_indicator[future]
                try:
                    result = future.result()
                    results[indicator_name] = result
                except Exception as e:
                    logging.error(f"Error calculating {indicator_name}: {str(e)}")
                    results[indicator_name] = None
        
        return results

# Global processor instance
processor = ParallelProcessor()