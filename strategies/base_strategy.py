# strategies/base_strategy.py
from abc import ABC, abstractmethod
import pandas as pd
import concurrent.futures
from config.symbols import SYMBOLS_CONFIG
from utils.helpers import get_symbol_type, get_stop_loss_pips
from utils.parallel_processor import processor

class BaseStrategy(ABC):
    def __init__(self, symbol=None, timeframe="M1"):
        self.symbol = symbol
        self.timeframe = timeframe
        self.data = None
        self.symbol_type = get_symbol_type(symbol) if symbol else None
        self.symbol_config = SYMBOLS_CONFIG.get(symbol, {}) if symbol else {}
    
    @abstractmethod
    def generate_signals(self, data):
        """Generate trading signals"""
        pass
    
    @abstractmethod
    def validate_signal(self, signal):
        """Validate signal before execution"""
        pass
    
    def get_market_data(self, bars=100):
        """Get market data - to be implemented by connector"""
        pass
    
    def get_symbol_stop_loss_pips(self):
        """Get symbol-specific stop loss pips"""
        return get_stop_loss_pips(self.symbol)
    
    def adjust_for_volatility(self, base_value):
        """Adjust values based on symbol volatility"""
        from config.settings import Config
        symbol_settings = Config.SYMBOL_SETTINGS.get(self.symbol, {})
        multiplier = symbol_settings.get('volatility_multiplier', 1.0)
        return base_value * multiplier
    
    def process_multiple_symbols(self, symbols, data_provider):
        """Process multiple symbols in parallel"""
        def process_single_symbol(symbol):
            data = data_provider.get_historical_data(symbol)
            if data is not None:
                signals = self.generate_signals(data)
                return {symbol: signals}
            return {symbol: []}
        
        # Process symbols in parallel
        results = processor.process_symbols_parallel(symbols, process_single_symbol)
        
        # Flatten results
        all_signals = []
        for symbol_signals in results.values():
            if symbol_signals:
                for signals in symbol_signals.values():
                    all_signals.extend(signals)
        
        return all_signals

class MultiSymbolStrategy(BaseStrategy):
    """Strategy that can process multiple symbols efficiently"""
    
    def __init__(self, symbols=None, timeframe="M1"):
        super().__init__(None, timeframe)
        self.symbols = symbols or []
    
    def process_all_symbols_parallel(self, data_provider, risk_manager):
        """Process all symbols in parallel and generate signals"""
        def process_symbol_with_context(symbol):
            # Get market data
            data = data_provider.get_historical_data(symbol)
            if data is None or len(data) < 50:  # Minimum data requirement
                return symbol, []
            
            # Generate signals
            signals = self.generate_signals(data)
            
            # Validate signals
            validated_signals = []
            for signal in signals:
                if self.validate_signal(signal):
                    # Add symbol and risk management info
                    signal['symbol'] = symbol
                    validated_signals.append(signal)
            
            return symbol, validated_signals
        
        # Process all symbols in parallel
        results = processor.process_symbols_parallel(self.symbols, process_symbol_with_context)
        
        # Collect all valid signals
        all_signals = []
        for symbol, signals in results.items():
            if signals:
                all_signals.extend(signals)
        
        return all_signals