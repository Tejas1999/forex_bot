# broker/order_manager.py
import MetaTrader5 as mt5
import logging
from config.settings import Config

class OrderManager:
    def __init__(self):
        self.magic_number = 234000
    
    def create_order_request(self, symbol, order_type, volume, price, sl=None, tp=None, comment=""):
        """Create order request dictionary"""
        if order_type == "BUY":
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": mt5.symbol_info_tick(symbol).ask if price is None else price,
                "sl": sl or 0,
                "tp": tp or 0,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
        else:  # SELL
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(symbol).bid if price is None else price,
                "sl": sl or 0,
                "tp": tp or 0,
                "deviation": 20,
                "magic": self.magic_number,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
        
        return request
    
    def place_order(self, request):
        """Place order with request"""
        try:
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Order failed: {result.retcode} - {result.comment}")
                return None
            
            logging.info(f"✅ Order placed: {result.order} - {result.comment}")
            return result
            
        except Exception as e:
            logging.error(f"Error placing order: {str(e)}")
            return None
    
    def modify_position(self, ticket, sl=None, tp=None):
        """Modify existing position"""
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return False
            
            position = position[0]
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "ticket": ticket,
                "sl": sl or position.sl,
                "tp": tp or position.tp,
            }
            
            result = mt5.order_send(request)
            return result.retcode == mt5.TRADE_RETCODE_DONE
            
        except Exception as e:
            logging.error(f"Error modifying position: {str(e)}")
            return False
    
    def close_position(self, ticket):
        """Close existing position"""
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return False
            
            position = position[0]
            
            # Create close request
            if position.type == mt5.ORDER_TYPE_BUY:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": position.symbol,
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "position": ticket,
                    "price": mt5.symbol_info_tick(position.symbol).bid,
                    "deviation": 20,
                    "magic": self.magic_number,
                    "comment": "Close position",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
            else:  # SELL position
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": position.symbol,
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "position": ticket,
                    "price": mt5.symbol_info_tick(position.symbol).ask,
                    "deviation": 20,
                    "magic": self.magic_number,
                    "comment": "Close position",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
            
            result = mt5.order_send(request)
            return result.retcode == mt5.TRADE_RETCODE_DONE
            
        except Exception as e:
            logging.error(f"Error closing position: {str(e)}")
            return False