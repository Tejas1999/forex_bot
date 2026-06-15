// Connect to SocketIO
const socket = io();

// Handle real-time updates
socket.on('status_update', updateDashboard);

// Utility: Format currency
function formatCurrency(value) {
    return '$' + parseFloat(value || 0).toFixed(2);
}

// Utility: Format percent
function formatPercent(value) {
    return `${parseFloat(value || 0).toFixed(2)}%`;
}

// Update dashboard with new data
function updateDashboard(data = {}) {
    // Bot status
    const status = data.status || (data.running ? 'start' : 'stop');
    localStorage.setItem('botStatus', status);
    const statusElement = document.getElementById('botStatus');
    const running = status === 'start';
    statusElement.innerHTML = `Bot Status: <span class="${running ? 'status-running' : 'status-stopped'}">${running ? '🟢 Running' : '🔴 Stopped'}</span>`;
    document.getElementById('startBtn').disabled = running;
    document.getElementById('stopBtn').disabled = !running;
    document.getElementById('refreshBtn').disabled = !running;

    // Symbols
    document.getElementById('symbolsList').innerHTML = (data.symbols || [])
        .map(symbol => `<span class="symbol-tag">${symbol}</span>`).join(' ') || '<span>No symbols</span>';

    // Account info
    document.getElementById('balance').textContent = formatCurrency(data.balance);
    document.getElementById('equity').textContent = formatCurrency(data.equity);
    document.getElementById('freeMargin').textContent = formatCurrency(data.free_margin);
    document.getElementById('positionCount').textContent = (data.positions || []).length;

    // Margin level
    document.getElementById('marginLevel').textContent = data.margin_level ? `Margin Level: ${formatPercent(data.margin_level)}` : 'Margin Level: N/A';

    // Positions
    const positionsBody = document.getElementById('positionsBody');
    if (data.positions && data.positions.length) {
        positionsBody.innerHTML = data.positions.map(pos => {
            const pnlClass = pos.pnl >= 0 ? 'pnl-positive' : 'pnl-negative';
            const pnlText = (pos.pnl >= 0 ? '+' : '') + (pos.pnl || 0).toFixed(2);
            return `
                <tr>
                    <td><span class="symbol-tag">${pos.symbol}</span></td>
                    <td>${pos.type}</td>
                    <td>${parseFloat(pos.lots || 0).toFixed(2)}</td>
                    <td>${parseFloat(pos.price || 0).toFixed(5)}</td>
                    <td>${pos.sl > 0 ? parseFloat(pos.sl).toFixed(5) : 'None'}</td>
                    <td>${pos.tp > 0 ? parseFloat(pos.tp).toFixed(5) : 'None'}</td>
                    <td class="${pnlClass}">${pnlText}</td>
                </tr>
            `;
        }).join('');
    } else {
        positionsBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No open positions</td></tr>';
    }

    // Logs
    const logEntries = document.getElementById('logEntries');
    logEntries.innerHTML = (data.logs || []).slice().reverse().map(log =>
        `<div class="log-entry">[${log.time}] ${log.message}</div>`
    ).join('');
    logEntries.scrollTop = logEntries.scrollHeight;
}

// API call helper
function apiCall(endpoint) {
    return fetch(endpoint, { method: 'GET', headers: { 'Content-Type': 'application/json' } })
        .then(res => res.json());
}

// Start bot
function startBot() {
    apiCall('/api/start')
        .then(data => console.log('Bot started:', data))
        .catch(error => console.error('Error starting bot:', error));
}

// Stop bot
function stopBot() {
    apiCall('/api/stop')
        .then(data => console.log('Bot stopped:', data))
        .catch(error => console.error('Error stopping bot:', error));
}

// Refresh data
function refreshData() {
    apiCall('/api/refresh')
        .then(data => console.log('Data refreshed:', data))
        .catch(error => console.error('Error refreshing data:', error));
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    apiCall('/api/status')
        .then(updateDashboard)
        .catch(error => {
            console.error('Error loading initial data:', error);
            const savedStatus = localStorage.getItem('botStatus') || 'stop';
            updateDashboard({ status: savedStatus, running: savedStatus === 'start' });
        });
});
