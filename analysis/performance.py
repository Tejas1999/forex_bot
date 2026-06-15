# analysis/performance.py
import pandas as pd
import numpy as np
from datetime import datetime
import logging

class PerformanceAnalyzer:
    def __init__(self):
        self.trades = []
        self.equity_curve = []
    
    def add_trade(self, trade):
        """Add trade to performance analyzer"""
        self.trades.append(trade)
    
    def calculate_metrics(self):
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            return {}
        
        # Convert trades to DataFrame
        df = pd.DataFrame(self.trades)
        df['cumulative_pnl'] = df['pnl'].cumsum()
        df['equity'] = 10000 + df['cumulative_pnl']  # Assuming 10000 initial capital
        
        # Basic metrics
        total_pnl = df['pnl'].sum()
        total_trades = len(df)
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] < 0]
        
        # Win rate
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        # Average win/loss
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0
        
        # Profit factor
        total_wins = winning_trades['pnl'].sum()
        total_losses = abs(losing_trades['pnl'].sum())
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Maximum drawdown
        df['peak'] = df['equity'].expanding().max()
        df['drawdown'] = (df['equity'] - df['peak']) / df['peak']
        max_drawdown = df['drawdown'].min()
        
        # Sharpe ratio (simplified)
        returns = df['pnl'] / 10000  # Assuming 10000 initial capital
        sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        # Consecutive wins/losses
        df['sign'] = np.sign(df['pnl'])
        df['group'] = (df['sign'] != df['sign'].shift()).cumsum()
        consecutive = df.groupby('group')['sign'].agg(['count', 'first'])
        max_consecutive_wins = consecutive[consecutive['first'] > 0]['count'].max() if len(consecutive[consecutive['first'] > 0]) > 0 else 0
        max_consecutive_losses = consecutive[consecutive['first'] < 0]['count'].max() if len(consecutive[consecutive['first'] < 0]) > 0 else 0
        
        return {
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'largest_win': winning_trades['pnl'].max() if len(winning_trades) > 0 else 0,
            'largest_loss': losing_trades['pnl'].min() if len(losing_trades) > 0 else 0
        }
    
    def generate_report(self):
        """Generate performance report"""
        metrics = self.calculate_metrics()
        
        report = f"""
Performance Report
==================
Total P&L: ${metrics.get('total_pnl', 0):.2f}
Total Trades: {metrics.get('total_trades', 0)}
Win Rate: {metrics.get('win_rate', 0)*100:.2f}%
Average Win: ${metrics.get('avg_win', 0):.2f}
Average Loss: ${metrics.get('avg_loss', 0):.2f}
Profit Factor: {metrics.get('profit_factor', 0):.2f}
Maximum Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%
Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}
Max Consecutive Wins: {metrics.get('max_consecutive_wins', 0)}
Max Consecutive Losses: {metrics.get('max_consecutive_losses', 0)}
Largest Win: ${metrics.get('largest_win', 0):.2f}
Largest Loss: ${metrics.get('largest_loss', 0):.2f}
        """
        
        return report