# database/market_logger.py
import sqlite3
import pandas as pd
from datetime import datetime
import logging
import os

class MarketLogger:
    def __init__(self, db_path="database/market_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize market data database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create market data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    bid REAL NOT NULL,
                    ask REAL NOT NULL,
                    last_price REAL,
                    volume REAL,
                    spread REAL
                )
            ''')
            
            # Create signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    price REAL NOT NULL,
                    indicator TEXT,
                    strength REAL,
                    confirmed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error initializing market database: {str(e)}")
    
    def log_market_data(self, symbol, bid, ask, last_price=None, volume=None):
        """Log current market data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            spread = abs(ask - bid) if bid and ask else 0
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO market_data 
                (timestamp, symbol, bid, ask, last_price, volume, spread)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                symbol,
                bid,
                ask,
                last_price,
                volume,
                spread
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error logging market data: {str(e)}")
    
    def log_signal(self, symbol, signal_type, price, indicator=None, strength=None):
        """Log trading signal"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO signals 
                (timestamp, symbol, signal_type, price, indicator, strength)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                symbol,
                signal_type,
                price,
                indicator,
                strength
            ))
            
            signal_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logging.info(f"🎯 Signal logged: {signal_type} for {symbol} at {price}")
            return signal_id
            
        except Exception as e:
            logging.error(f"Error logging signal: {str(e)}")
            return None
    
    def get_market_history(self, symbol, hours=24):
        """Get market data history"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            since_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            query = '''
                SELECT * FROM market_data 
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, since_time))
            conn.close()
            
            return df
            
        except Exception as e:
            logging.error(f"Error getting market history: {str(e)}")
            return pd.DataFrame()
    
    def get_signal_history(self, symbol, days=7):
        """Get signal history"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            since_time = datetime.now() - pd.Timedelta(days=days)
            
            query = '''
                SELECT * FROM signals 
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, since_time))
            conn.close()
            
            return df
            
        except Exception as e:
            logging.error(f"Error getting signal history: {str(e)}")
            return pd.DataFrame()