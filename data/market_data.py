# data/market_data.py
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import logging

class MarketData:
    def __init__(self):
        self.cache = {}
    
    def get_current_price(self, symbol):
        """Get current market price"""
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
            
            return {
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'time': datetime.fromtimestamp(tick.time)
            }
            
        except Exception as e:
            logging.error(f"Error getting current price for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, timeframe=mt5.TIMEFRAME_M1, count=1000):
        """Get historical market data"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{timeframe}_{count}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < timedelta(minutes=1):
                    return cached_data
            
            # Get data from MT5
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Cache the data
            self.cache[cache_key] = (df, datetime.now())
            
            return df
            
        except Exception as e:
            logging.error(f"Error getting historical data for {symbol}: {str(e)}")
            return None
    
    def get_symbol_info(self, symbol):
        """Get symbol information"""
        try:
            info = mt5.symbol_info(symbol)
            if info is None:
                return None
            
            return {
                'symbol': info.name,
                'digits': info.digits,
                'point': info.point,
                'spread': info.spread,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'volume_step': info.volume_step,
                'tick_value': info.trade_tick_value,
                'tick_size': info.trade_tick_size
            }
            
        except Exception as e:
            logging.error(f"Error getting symbol info for {symbol}: {str(e)}")
            return None