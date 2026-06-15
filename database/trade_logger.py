# database/trade_logger.py
import sqlite3
import pandas as pd
from datetime import datetime
import logging
import os

class TradeLogger:
    def __init__(self, db_path="database/trades.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize trades database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    lot_size REAL NOT NULL,
                    stop_loss REAL,
                    take_profit REAL,
                    pnl REAL,
                    status TEXT NOT NULL,
                    strategy TEXT,
                    comments TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error initializing trade database: {str(e)}")
    
    def log_trade_open(self, trade_data):
        """Log opened trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades 
                (timestamp, symbol, order_type, entry_price, lot_size, 
                 stop_loss, take_profit, pnl, status, strategy, comments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                trade_data.get('symbol', ''),
                trade_data.get('type', ''),
                trade_data.get('entry_price', 0),
                trade_data.get('lot_size', 0),
                trade_data.get('stop_loss', 0),
                trade_data.get('take_profit', 0),
                0,  # PNL starts at 0
                'OPEN',
                trade_data.get('strategy', ''),
                trade_data.get('comments', '')
            ))
            
            trade_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logging.info(f"📝 Trade logged: {trade_id} - {trade_data.get('type')} {trade_data.get('symbol')}")
            return trade_id
            
        except Exception as e:
            logging.error(f"Error logging trade: {str(e)}")
            return None
    
    def log_trade_close(self, trade_id, exit_price, pnl):
        """Log closed trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE trades 
                SET exit_price = ?, pnl = ?, status = ?
                WHERE id = ?
            ''', (exit_price, pnl, 'CLOSED', trade_id))
            
            conn.commit()
            conn.close()
            
            logging.info(f"📝 Trade closed: {trade_id} - PNL: ${pnl:.2f}")
            
        except Exception as e:
            logging.error(f"Error closing trade log: {str(e)}")
    
    def get_recent_trades(self, limit=50):
        """Get recent trades"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(limit,))
            conn.close()
            
            return df
            
        except Exception as e:
            logging.error(f"Error getting recent trades: {str(e)}")
            return pd.DataFrame()
    
    def get_trades_by_date(self, start_date, end_date):
        """Get trades within date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM trades 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            conn.close()
            
            return df
            
        except Exception as e:
            logging.error(f"Error getting trades by date: {str(e)}")
            return pd.DataFrame()