# utils/cpu_monitor.py
import psutil
import threading
import time
import logging
from datetime import datetime

class CPUMonitor:
    def __init__(self, interval=5):
        self.interval = interval
        self.monitoring = False
        self.cpu_percentages = []
        self.memory_usage = []
        
    def start_monitoring(self):
        """Start CPU monitoring in background thread"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop CPU monitoring"""
        self.monitoring = False
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Get CPU and memory usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                self.cpu_percentages.append(cpu_percent)
                self.memory_usage.append(memory_percent)
                
                # Keep only last 100 readings
                if len(self.cpu_percentages) > 100:
                    self.cpu_percentages.pop(0)
                if len(self.memory_usage) > 100:
                    self.memory_usage.pop(0)
                
                # Log if CPU usage is high
                if cpu_percent > 80:
                    logging.warning(f"⚠️  High CPU usage: {cpu_percent}%")
                if memory_percent > 85:
                    logging.warning(f"⚠️  High Memory usage: {memory_percent}%")
                
                time.sleep(self.interval)
                
            except Exception as e:
                logging.error(f"❌ Error in CPU monitoring: {str(e)}")
                time.sleep(self.interval)
    
    def get_stats(self):
        """Get current performance statistics"""
        if not self.cpu_percentages:
            return {}
        
        return {
            'avg_cpu_percent': sum(self.cpu_percentages) / len(self.cpu_percentages),
            'current_cpu_percent': self.cpu_percentages[-1] if self.cpu_percentages else 0,
            'max_cpu_percent': max(self.cpu_percentages),
            'avg_memory_percent': sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0,
            'current_memory_percent': self.memory_usage[-1] if self.memory_usage else 0
        }
    
    def log_performance_report(self):
        """Log detailed performance report"""
        stats = self.get_stats()
        if stats:
            report = f"""
📊 Performance Report:
   Average CPU: {stats['avg_cpu_percent']:.1f}%
   Current CPU: {stats['current_cpu_percent']:.1f}%
   Peak CPU: {stats['max_cpu_percent']:.1f}%
   Memory Usage: {stats['avg_memory_percent']:.1f}%
            """
            logging.info(report)

# Global CPU monitor instance
cpu_monitor = CPUMonitor()

# Start monitoring when module is imported
cpu_monitor.start_monitoring()