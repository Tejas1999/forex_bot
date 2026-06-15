# web/routes/dashboard_routes.py
from flask import Blueprint, render_template, jsonify
import threading
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

# Global references (set from main.py)
bot_thread = None
trading_bot = None
bot_status = {}
socketio_instance = None

def set_globals(thread, bot, status, socketio):
    global bot_thread, trading_bot, bot_status, socketio_instance
    bot_thread = thread
    trading_bot = bot
    bot_status = status
    socketio_instance = socketio

@dashboard_bp.route('/')
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/start')
def start_bot_api():
    global bot_thread, trading_bot, bot_status, socketio_instance

    if not bot_thread or not bot_thread.is_alive():
        try:
            from main import TradingBot
        except ImportError:
            import sys, os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from main import TradingBot

        trading_bot = TradingBot()
        bot_thread = threading.Thread(target=trading_bot.run, daemon=True)
        bot_thread.start()
        bot_status.setdefault('logs', []).append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': 'Bot started from web dashboard'
        })
        bot_status['running'] = True
        bot_status['status'] = 'start'

        if socketio_instance:
            try:
                socketio_instance.emit('status_update', bot_status)
            except Exception as e:
                print(f"SocketIO emit error (start): {e}")

        return jsonify({'success': True, 'message': 'Bot started'})
    return jsonify({'success': False, 'message': 'Bot already running'})

@dashboard_bp.route('/api/stop')
def stop_bot_api():
    global trading_bot, bot_status, socketio_instance

    if trading_bot:
        trading_bot.stop()
        bot_status.setdefault('logs', []).append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': 'Bot stopped from web dashboard'
        })
        bot_status['running'] = False
        bot_status['status'] = 'stop'

        if socketio_instance:
            try:
                socketio_instance.emit('status_update', bot_status)
            except Exception as e:
                print(f"SocketIO emit error (stop): {e}")

        return jsonify({'success': True, 'message': 'Bot stopped'})
    return jsonify({'success': False, 'message': 'Bot not running'})

@dashboard_bp.route('/api/status')
def get_status():
    global bot_status
    return jsonify(bot_status)

@dashboard_bp.route('/api/refresh')
def refresh_data():
    global trading_bot, bot_status

    if trading_bot and bot_status.get('running', False):
        try:
            trading_bot.update_dashboard_data()
            return jsonify({'success': True, 'message': 'Data refreshed'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error refreshing data: {e}'})
    return jsonify({'success': False, 'message': 'Bot not running'})
