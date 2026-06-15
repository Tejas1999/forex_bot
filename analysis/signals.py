# analysis/signals.py
import pandas as pd
import numpy as np
from datetime import datetime
import logging

class SignalAnalyzer:
    def __init__(self):
        self.signals = []
        self.signal_performance = {}
    
    def add_signal(self, signal, result):
        """Add signal and its result for analysis"""
        signal_data = {
            'signal': signal,
            'result': result,
            'timestamp': datetime.now()
        }
        self.signals.append(signal_data)
    
    def analyze_signal_performance(self):
        """Analyze performance of different signal types"""
        if not self.signals:
            return {}
        
        df = pd.DataFrame(self.signals)
        
        # Group by signal type and calculate performance
        performance = {}
        for signal_type in df['signal'].apply(lambda x: x.get('type', 'UNKNOWN')).unique():
            signal_trades = [s for s in self.signals 
                           if s['signal'].get('type') == signal_type]
            
            if signal_trades:
                results = [s['result'] for s in signal_trades]
                win_rate = len([r for r in results if r > 0]) / len(results)
                avg_return = np.mean(results)
                total_trades = len(results)
                
                performance[signal_type] = {
                    'win_rate': win_rate,
                    'avg_return': avg_return,
                    'total_trades': total_trades
                }
        
        return performance
    
    def get_best_signals(self, min_trades=10):
        """Get best performing signals"""
        performance = self.analyze_signal_performance()
        
        # Filter signals with minimum trades
        filtered_signals = {k: v for k, v in performance.items() 
                          if v['total_trades'] >= min_trades}
        
        # Sort by win rate
        sorted_signals = sorted(filtered_signals.items(), 
                              key=lambda x: x[1]['win_rate'], reverse=True)
        
        return sorted_signals
    
    def generate_signal_report(self):
        """Generate signal analysis report"""
        performance = self.analyze_signal_performance()
        
        report = "Signal Performance Report\n========================\n"
        
        for signal_type, metrics in performance.items():
            report += f"\n{signal_type}:\n"
            report += f"  Win Rate: {metrics['win_rate']*100:.2f}%\n"
            report += f"  Average Return: ${metrics['avg_return']:.2f}\n"
            report += f"  Total Trades: {metrics['total_trades']}\n"
        
        return report