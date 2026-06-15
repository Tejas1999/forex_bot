# config/symbols.py
SYMBOLS_CONFIG = {
 "EURUSD": {
        "pip_size": 0.0001,
        "lot_size": 0.01,
        "spread_limit": 2.0,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "forex"
    },
    "GBPUSD": {
        "pip_size": 0.0001,
        "lot_size": 0.01,
        "spread_limit": 2.5,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "forex"
    },
    "USDJPY": {
        "pip_size": 0.01,
        "lot_size": 0.01,
        "spread_limit": 1.5,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "forex"
    },
    "AUDUSD": {
        "pip_size": 0.0001,
        "lot_size": 0.01,
        "spread_limit": 3.0,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "forex"
    },
    "USDCAD": {
        "pip_size": 0.0001,
        "lot_size": 0.01,
        "spread_limit": 2.0,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "forex"
    },
    # Cryptocurrency symbols
    "BTCUSDM": {
        "pip_size": 0.1,
        "lot_size": 0.01,
        "spread_limit": 50.0,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "crypto",
        "contract_size": 1.0,
        "price_precision": 2
    },
    "BTCUSD": {
        "pip_size": 0.1,
        "lot_size": 0.01,
        "spread_limit": 50.0,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "crypto",
        "contract_size": 1.0,
        "price_precision": 2
    },
    "ETHUSDM": {
        "pip_size": 0.01,
        "lot_size": 0.01,
        "spread_limit": 10.0,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "crypto",
        "contract_size": 1.0,
        "price_precision": 2
    },
    # Commodity symbols
    "USOILM": {
        "pip_size": 0.01,
        "lot_size": 0.1,
        "spread_limit": 0.1,
        "min_volume": 0.1,
        "max_volume": 10.0,
        "symbol_type": "commodity",
        "contract_size": 100.0,
        "price_precision": 2
    },
    "GOLD": {
        "pip_size": 0.1,
        "lot_size": 0.01,
        "spread_limit": 0.5,
        "min_volume": 0.01,
        "max_volume": 1.0,
        "symbol_type": "commodity",
        "contract_size": 100.0,
        "price_precision": 2
    },
    "SILVER": {
        "pip_size": 0.001,
        "lot_size": 0.1,
        "spread_limit": 0.05,
        "min_volume": 0.1,
        "max_volume": 10.0,
        "symbol_type": "commodity",
        "contract_size": 5000.0,
        "price_precision": 3
    }
}

# Symbol categories
MAJOR_PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
MINOR_PAIRS = ["EURGBP", "GBPJPY", "AUDJPY", "NZDUSD"]
CRYPTO_PAIRS = ["BTCUSDM", "ETHUSDM"]
COMMODITY_PAIRS = ["USOILM", "GOLD", "SILVER"]
EXOTIC_PAIRS = ["USDMXN", "USDZAR", "USDTRY"]

# All tradable symbols
ALL_SYMBOLS = list(SYMBOLS_CONFIG.keys())

# Symbol type groups
SYMBOL_TYPES = {
    "forex": [sym for sym, config in SYMBOLS_CONFIG.items() if config["symbol_type"] == "forex"],
    "crypto": [sym for sym, config in SYMBOLS_CONFIG.items() if config["symbol_type"] == "crypto"],
    "commodity": [sym for sym, config in SYMBOLS_CONFIG.items() if config["symbol_type"] == "commodity"]
}