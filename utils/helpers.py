# utils/helpers.py
import math
from config.symbols import SYMBOLS_CONFIG

def format_price(price, symbol):
    """Format price to appropriate decimal places for symbol"""
    symbol_config = SYMBOLS_CONFIG.get(symbol, {})
    price_precision = symbol_config.get('price_precision', 5)
    
    if 'price_precision' in symbol_config:
        return f"{price:.{price_precision}f}"
    elif symbol.endswith("JPY"):
        return f"{price:.3f}"
    else:
        return f"{price:.5f}"

def calculate_pip_value(symbol, lot_size, exchange_rate=1.0):
    """Calculate pip value for symbol"""
    symbol_config = SYMBOLS_CONFIG.get(symbol, {})
    
    if 'contract_size' in symbol_config:
        # For crypto and commodities
        contract_size = symbol_config['contract_size']
        pip_size = symbol_config['pip_size']
        pip_value = (pip_size / exchange_rate) * lot_size * contract_size
    elif symbol.endswith("JPY"):
        pip_value = (0.01 / exchange_rate) * lot_size * 100000
    else:
        pip_value = (0.0001 / exchange_rate) * lot_size * 100000
    
    return round(pip_value, 2)

def get_pip_size(symbol):
    """Get pip size for symbol"""
    symbol_config = SYMBOLS_CONFIG.get(symbol, {})
    return symbol_config.get('pip_size', 0.0001)

def calculate_distance(price1, price2, symbol):
    """Calculate distance in pips between two prices"""
    pip_size = get_pip_size(symbol)
    return abs(price1 - price2) / pip_size

def normalize_lot_size(lot_size, symbol):
    """Normalize lot size to symbol-specific values"""
    symbol_config = SYMBOLS_CONFIG.get(symbol, {})
    min_lot = symbol_config.get('min_volume', 0.01)
    max_lot = symbol_config.get('max_volume', 1.0)
    step = 0.01
    
    lot_size = max(min_lot, min(lot_size, max_lot))
    return round(lot_size / step) * step

def get_symbol_type(symbol):
    """Get symbol type (forex, crypto, commodity)"""
    symbol_config = SYMBOLS_CONFIG.get(symbol, {})
    return symbol_config.get('symbol_type', 'forex')

def get_stop_loss_pips(symbol, default_value=20):
    """Get symbol-specific stop loss pips"""
    from config.settings import Config
    symbol_type = get_symbol_type(symbol)
    return Config.STOP_LOSS_PIPS.get(symbol_type, default_value)