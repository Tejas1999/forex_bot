# web/dashboard.py
from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to store bot data
bot_status = {
    'running': False,
    'balance': 10000.00,
    'equity': 10000.00,
    'free_margin': 10000.00,
    'positions': [],
    'logs': []
}

class WebDashboard:
    def start_bot_callback(self):
        bot_status['running'] = True
        bot_status['logs'].append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': 'Bot started from web dashboard'
        })
        socketio.emit('status_update', bot_status)
        return True

    def stop_bot_callback(self):
        bot_status['running'] = False
        bot_status['logs'].append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': 'Bot stopped from web dashboard'
        })
        socketio.emit('status_update', bot_status)
        return True

@app.route('/')
def index():
    return dashboard_template()

@app.route('/api/status')
def get_status():
    return jsonify(bot_status)

@app.route('/api/start', methods=['POST'])
def start_bot():
    dashboard = WebDashboard()
    if dashboard.start_bot_callback():
        return jsonify({'success': True, 'message': 'Bot started'})
    return jsonify({'success': False, 'message': 'Failed to start bot'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    dashboard = WebDashboard()
    if dashboard.stop_bot_callback():
        return jsonify({'success': True, 'message': 'Bot stopped'})
    return jsonify({'success': False, 'message': 'Failed to stop bot'})

@socketio.on('connect')
def handle_connect():
    emit('status_update', bot_status)

@socketio.on('disconnect')
def handle_disconnect():
    pass

def update_dashboard_data():
    while True:
        if bot_status['running']:
            bot_status['equity'] = round(10000 + (time.time() % 100), 2)
            bot_status['free_margin'] = round(bot_status['equity'] * 0.8, 2)
            bot_status['positions'] = [
                {
                    'symbol': 'EURUSD',
                    'type': 'BUY',
                    'lots': 0.01,
                    'price': 1.1050,
                    'sl': 1.1030,
                    'tp': 1.1090,
                    'pnl': round((time.time() % 5) - 2.5, 2)
                },
                {
                    'symbol': 'GBPUSD',
                    'type': 'SELL',
                    'lots': 0.02,
                    'price': 1.2500,
                    'sl': 1.2520,
                    'tp': 1.2460,
                    'pnl': round((time.time() % 3) - 1.5, 2)
                }
            ]
            if len(bot_status['logs']) == 0 or time.time() % 10 < 1:
                bot_status['logs'].append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'message': f'Dashboard updated - Equity: ${bot_status["equity"]}'
                })
                if len(bot_status['logs']) > 50:
                    bot_status['logs'] = bot_status['logs'][-50:]
            socketio.emit('status_update', bot_status)
        time.sleep(2)

def dashboard_template():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Forex Trading Bot Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .status-panel { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .account-info { display: flex; justify-content: space-between; flex-wrap: wrap; }
        .info-item { background: #ecf0f1; padding: 15px; border-radius: 8px; margin: 5px; flex: 1; min-width: 200px; }
        .controls { text-align: center; margin: 20px 0; }
        .btn { padding: 12px 24px; margin: 0 10px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn-start { background: #27ae60; color: white; }
        .btn-stop { background: #e74c3c; color: white; }
        .btn:disabled { background: #95a5a6; cursor: not-allowed; }
        .positions-table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .positions-table th, .positions-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .positions-table th { background: #34495e; color: white; }
        .positions-table tr:hover { background-color: #f8f9fa; }
        .log-panel { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-top: 20px; }
        .log-entries { height: 300px; overflow-y: auto; background: #2c3e50; color: white; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px; }
        .log-entry { margin: 5px 0; }
        .status-running { color: #27ae60; font-weight: bold; }
        .status-stopped { color: #e74c3c; font-weight: bold; }
        .pnl-positive { color: #27ae60; }
        .pnl-negative { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Forex Trading Bot Dashboard</h1>
            <div id="botStatus" class="status-stopped">Bot Status: Stopped</div>
        </div>
        <div class="status-panel">
            <h2>Account Information</h2>
            <div class="account-info">
                <div class="info-item">
                    <h3>Balance</h3>
                    <div id="balance">$10,000.00</div>
                </div>
                <div class="info-item">
                    <h3>Equity</h3>
                    <div id="equity">$10,000.00</div>
                </div>
                <div class="info-item">
                    <h3>Free Margin</h3>
                    <div id="freeMargin">$10,000.00</div>
                </div>
                <div class="info-item">
                    <h3>Positions</h3>
                    <div id="positionCount">0</div>
                </div>
            </div>
        </div>
        <div class="controls">
            <button id="startBtn" class="btn btn-start" onclick="startBot()">Start Bot</button>
            <button id="stopBtn" class="btn btn-stop" onclick="stopBot()" disabled>Stop Bot</button>
        </div>
        <div class="status-panel">
            <h2>Open Positions</h2>
            <table class="positions-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Type</th>
                        <th>Lots</th>
                        <th>Price</th>
                        <th>SL</th>
                        <th>TP</th>
                        <th>PNL</th>
                    </tr>
                </thead>
                <tbody id="positionsBody">
                    <tr><td colspan="7" style="text-align: center;">No open positions</td></tr>
                </tbody>
            </table>
        </div>
        <div class="log-panel">
            <h2>Activity Log</h2>
            <div class="log-entries" id="logEntries">
                <div class="log-entry">Dashboard initialized</div>
            </div>
        </div>
    </div>
    <script>
        const socket = io();
        socket.on('status_update', function(data) {
            updateDashboard(data);
        });
        function updateDashboard(data) {
            const statusElement = document.getElementById('botStatus');
            if (data.running) {
                statusElement.innerHTML = 'Bot Status: <span class="status-running">Running</span>';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            } else {
                statusElement.innerHTML = 'Bot Status: <span class="status-stopped">Stopped</span>';
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
            document.getElementById('balance').textContent = '$' + parseFloat(data.balance).toFixed(2);
            document.getElementById('equity').textContent = '$' + parseFloat(data.equity).toFixed(2);
            document.getElementById('freeMargin').textContent = '$' + parseFloat(data.free_margin).toFixed(2);
            const positionsBody = document.getElementById('positionsBody');
            if (data.positions && data.positions.length > 0) {
                positionsBody.innerHTML = '';
                data.positions.forEach(pos => {
                    const row = document.createElement('tr');
                    const pnlClass = pos.pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
                    row.innerHTML = `
                        <td>${pos.symbol}</td>
                        <td>${pos.type}</td>
                        <td>${pos.lots}</td>
                        <td>${pos.price}</td>
                        <td>${pos.sl}</td>
                        <td>${pos.tp}</td>
                        <td class="${pnlClass}">${pos.pnl >= 0 ? '+' : ''}${pos.pnl}</td>
                    `;
                    positionsBody.appendChild(row);
                });
                document.getElementById('positionCount').textContent = data.positions.length;
            } else {
                positionsBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No open positions</td></tr>';
                document.getElementById('positionCount').textContent = '0';
            }
            const logEntries = document.getElementById('logEntries');
            if (data.logs && data.logs.length > 0) {
                logEntries.innerHTML = '';
                data.logs.slice().reverse().forEach(log => {
                    const logEntry = document.createElement('div');
                    logEntry.className = 'log-entry';
                    logEntry.textContent = `[${log.time}] ${log.message}`;
                    logEntries.appendChild(logEntry);
                });
                logEntries.scrollTop = logEntries.scrollHeight;
            }
        }
        function startBot() {
            fetch('/api/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    console.log('Start response:', data);
                })
                .catch(error => {
                    console.error('Error starting bot:', error);
                });
        }
        function stopBot() {
            fetch('/api/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    console.log('Stop response:', data);
                })
                .catch(error => {
                    console.error('Error stopping bot:', error);
                });
        }
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    update_thread = threading.Thread(target=update_dashboard_data, daemon=True)
    update_thread.start()
    print("Starting web dashboard at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
