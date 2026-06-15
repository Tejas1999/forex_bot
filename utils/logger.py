# utils/logger.py
import logging
import os
from datetime import datetime
from config.settings import Config

def setup_logger():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def log_trade(trade_info):
    """Log trade information"""
    logger = logging.getLogger(__name__)
    logger.info(f"TRADE: {trade_info}")