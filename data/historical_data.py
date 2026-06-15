# data/historical_data.py
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import logging
import os

class HistoricalData:
    def __init__(self, db_path="data/historical_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table for historical data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    UNIQUE(symbol, timeframe, timestamp)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
    
    def save_historical_data(self, symbol, timeframe, data):
        """Save historical data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            for _, row in data.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO market_data 
                    (symbol, timeframe, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, str(timeframe), row['time'], 
                    row['open'], row['high'], row['low'], row['close'], row['volume']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error saving historical data: {str(e)}")
    
    def load_historical_data(self, symbol, timeframe, days=30):
        """Load historical data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            since_date = datetime.now() - timedelta(days=days)
            
            query = '''
                SELECT * FROM market_data 
                WHERE symbol = ? AND timeframe = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, str(timeframe), since_date))
            conn.close()
            
            if not df.empty:
                df['time'] = pd.to_datetime(df['timestamp'])
                df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except Exception as e:
            logging.error(f"Error loading historical data: {str(e)}")
            return pd.DataFrame()
    
    def download_and_save_data(self, symbol, timeframe=mt5.TIMEFRAME_M1, days=30):
        """Download data from MT5 and save to database"""
        try:
            # Calculate date range
            from_date = datetime.now() - timedelta(days=days)
            
            # Get data from MT5
            rates = mt5.copy_rates_from(symbol, timeframe, from_date, 99999)
            if rates is None:
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Save to database
            self.save_historical_data(symbol, timeframe, df)
            
            logging.info(f"Saved {len(df)} records for {symbol}")
            return True
            
        except Exception as e:
            logging.error(f"Error downloading data for {symbol}: {str(e)}")
            return False