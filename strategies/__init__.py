# strategies/__init__.py
from .base_strategy import BaseStrategy
from .ma_crossover import MACrossoverStrategy
from .rsi_strategy import RSIStrategy
from .breakout_strategy import BreakoutStrategy
from .scalping_strategy import ScalpingStrategy

__all__ = [
    'BaseStrategy',
    'MACrossoverStrategy',
    'RSIStrategy',
    'BreakoutStrategy',
    'ScalpingStrategy'
]