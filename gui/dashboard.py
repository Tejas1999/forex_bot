# gui/dashboard.py
import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
import logging

class TradingDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forex Trading Bot Dashboard")
        self.root.geometry("800x600")
        
        self.setup_ui()
        self.running = False
        self.update_thread = None
    
    def setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Bot Status", padding="10")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Stopped", foreground="red")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.start_button = ttk.Button(status_frame, text="Start Bot", command=self.start_bot)
        self.start_button.grid(row=0, column=1, padx=(10, 0))
        
        self.stop_button = ttk.Button(status_frame, text="Stop Bot", command=self.stop_bot, state="disabled")
        self.stop_button.grid(row=0, column=2, padx=(10, 0))
        
        # Account info frame
        account_frame = ttk.LabelFrame(main_frame, text="Account Information", padding="10")
        account_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.balance_label = ttk.Label(account_frame, text="Balance: $0.00")
        self.balance_label.grid(row=0, column=0, sticky=tk.W)
        
        self.equity_label = ttk.Label(account_frame, text="Equity: $0.00")
        self.equity_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.margin_label = ttk.Label(account_frame, text="Free Margin: $0.00")
        self.margin_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Positions frame
        positions_frame = ttk.LabelFrame(main_frame, text="Open Positions", padding="10")
        positions_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(0, 10))
        
        self.positions_tree = ttk.Treeview(positions_frame, columns=("Symbol", "Type", "Lots", "Price", "SL", "TP"), show="headings", height=5)
        
        for col in self.positions_tree["columns"]:
            self.positions_tree.heading(col, text=col)
            self.positions_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(positions_frame, orient="vertical", command=self.positions_tree.yview)
        self.positions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.positions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=10, width=80)
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        account_frame.columnconfigure(0, weight=1)
        positions_frame.columnconfigure(0, weight=1)
        positions_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def start_bot(self):
        """Start trading bot"""
        self.running = True
        self.status_label.config(text="Running", foreground="green")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_dashboard, daemon=True)
        self.update_thread.start()
        
        logging.info("Bot started from dashboard")
    
    def stop_bot(self):
        """Stop trading bot"""
        self.running = False
        self.status_label.config(text="Stopped", foreground="red")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        logging.info("Bot stopped from dashboard")
    
    def update_dashboard(self):
        """Update dashboard information"""
        while self.running:
            try:
                # Update account info (placeholder)
                self.balance_label.config(text=f"Balance: ${10000.00:.2f}")
                self.equity_label.config(text=f"Equity: ${10050.25:.2f}")
                self.margin_label.config(text=f"Free Margin: ${8000.00:.2f}")
                
                # Update positions (placeholder)
                for item in self.positions_tree.get_children():
                    self.positions_tree.delete(item)
                
                # Add sample positions
                sample_positions = [
                    ("EURUSD", "BUY", "0.01", "1.1050", "1.1030", "1.1090"),
                    ("GBPUSD", "SELL", "0.02", "1.2500", "1.2520", "1.2460")
                ]
                
                for pos in sample_positions:
                    self.positions_tree.insert("", "end", values=pos)
                
                # Add log entry
                self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Dashboard updated\n")
                self.log_text.see(tk.END)
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logging.error(f"Error updating dashboard: {str(e)}")
                time.sleep(5)
    
    def add_log_entry(self, message):
        """Add entry to log"""
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
    
    def run(self):
        """Run the dashboard"""
        self.root.mainloop()

# Simple usage example
if __name__ == "__main__":
    dashboard = TradingDashboard()
    dashboard.run()