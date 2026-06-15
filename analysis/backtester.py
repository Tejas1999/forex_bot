# analysis/backtester.py
import pandas as pd
import numpy as np
from datetime import datetime
import logging

class Backtester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, strategy, data):
        """Run backtest on strategy with historical data"""
        try:
            # Generate signals
            signals = strategy.generate_signals(data)
            
            # Process signals
            for signal in signals:
                if signal['type'] == 'BUY':
                    self._execute_buy(signal)
                elif signal['type'] == 'SELL':
                    self._execute_sell(signal)
            
            # Close all positions at the end
            self._close_all_positions(data.iloc[-1]['close'])
            
            # Calculate performance metrics
            performance = self._calculate_performance()
            
            return {
                'trades': self.trades,
                'performance': performance,
                'equity_curve': self.equity_curve
            }
            
        except Exception as e:
            logging.error(f"Error in backtest: {str(e)}")
            return None
    
    def _execute_buy(self, signal):
        """Execute buy order"""
        position = {
            'type': 'BUY',
            'symbol': signal['symbol'],
            'entry_price': signal['entry_price'],
            'time': datetime.now(),
            'size': 0.01  # Fixed lot size for backtest
        }
        
        self.positions.append(position)
    
    def _execute_sell(self, signal):
        """Execute sell order"""
        position = {
            'type': 'SELL',
            'symbol': signal['symbol'],
            'entry_price': signal['entry_price'],
            'time': datetime.now(),
            'size': 0.01  # Fixed lot size for backtest
        }
        
        self.positions.append(position)
    
    def _close_all_positions(self, final_price):
        """Close all open positions"""
        for position in self.positions:
            if position['type'] == 'BUY':
                pnl = (final_price - position['entry_price']) * position['size'] * 100000
            else:  # SELL
                pnl = (position['entry_price'] - final_price) * position['size'] * 100000
            
            self.capital += pnl
            self.trades.append({
                'type': position['type'],
                'entry_price': position['entry_price'],
                'exit_price': final_price,
                'pnl': pnl,
                'time': position['time']
            })
        
        self.positions.clear()
    
    def _calculate_performance(self):
        """Calculate performance metrics"""
        if not self.trades:
            return {}
        
        total_pnl = sum(trade['pnl'] for trade in self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losing_trades])) if losing_trades else 0
        profit_factor = avg_win / avg_loss if avg_loss > 0 else float('inf')
        
        return {
            'total_pnl': total_pnl,
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'final_capital': self.capital,
            'return_percent': ((self.capital - self.initial_capital) / self.initial_capital) * 100
        }