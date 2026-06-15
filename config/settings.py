# config/settings.py
import os
from datetime import datetime

class Config:
    # Trading Settings
    SYMBOLS = ["BTCUSD"]  # Focus on BTCUSD for realtime run
    LOT_SIZE = 0.01
    MAX_RISK_PERCENT = 2.0
    MAX_POSITIONS = 5
    CHECK_INTERVAL = 20  # seconds
    
    # Risk Management
    STOP_LOSS_PIPS = {
        "forex": 20,
        "crypto": 50,
        "commodity": 30,
        "default": 20
    }
    TAKE_PROFIT_PIPS = {
        "forex": 40,
        "crypto": 100,
        "commodity": 60,
        "default": 40
    }
    TRAILING_STOP_PIPS = {
        "forex": 15,
        "crypto": 25,
        "commodity": 20,
        "default": 15
    }
    
    # Strategy Settings
    MA_FAST_PERIOD = 20
    MA_SLOW_PERIOD = 50
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    # MT5 Settings
    MT5_PATH = ""  # Leave empty for default
    LOGIN = 0
    PASSWORD = ""
    SERVER = ""
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Email Alerts (optional)
    EMAIL_ENABLED = False
    EMAIL_HOST = ""
    EMAIL_PORT = 587
    EMAIL_USER = ""
    EMAIL_PASS = ""
    
    # Symbol-specific settings
    SYMBOL_SETTINGS = {
        "BTCUSDM": {
            "volatility_multiplier": 2.0,
            "min_lot_size": 0.01
        },
        "ETHUSDM": {
            "volatility_multiplier": 1.8,
            "min_lot_size": 0.01
        },
        "USOILM": {
            "volatility_multiplier": 1.5,
            "min_lot_size": 0.1
        }
    }