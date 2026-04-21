// ═══════════════════════════════════════════════
// CyberShield AI — Frontend Logic
// ═══════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initButtons();
    initSidebar();
    checkDB();
    loadAnalytics();
    loadHistory();
});

// ─── Tab Switching ───
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const target = document.getElementById('tab-' + tab.dataset.tab);
            if (target) target.classList.add('active');
            if (tab.dataset.tab === 'analytics') loadAnalytics();
            if (tab.dataset.tab === 'history') loadHistory();
            if (tab.dataset.tab === 'models') loadModels();
        });
    });
}

// ─── Mobile Sidebar ───
function initSidebar() {
    const toggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle) {
        toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    }
}

// ─── Buttons ───
function initButtons() {
    document.getElementById('analyzeBtn').addEventListener('click', analyze);
    document.getElementById('resetBtn').addEventListener('click', () => {
        document.getElementById('predictForm').reset();
        document.getElementById('resultArea').classList.add('hidden');
    });
}

// ─── Check DB status ───
function checkDB() {
    fetch('/api/history?limit=1')
        .then(r => r.json())
        .then(d => {
            const el = document.getElementById('dbStatusText');
            if (d.error) {
                el.textContent = '❌ Disconnected';
            } else {
                el.textContent = '✅ Connected';
            }
        })
        .catch(() => {
            document.getElementById('dbStatusText').textContent = '❌ Disconnected';
        });
}

// ─── Analyze Traffic ───
async function analyze() {
    const btn = document.getElementById('analyzeBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> ANALYZING...';

    const form = document.getElementById('predictForm');
    const formData = new FormData(form);
    const data = {};
    formData.forEach((v, k) => { data[k] = parseFloat(v) || 0; });

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();

        if (result.error) {
            showToast('Error: ' + result.error, 'error');
            return;
        }

        const area = document.getElementById('resultArea');
        area.classList.remove('hidden');

        const isAttack = result.prediction === 1;
        area.innerHTML = `
            <div class="prediction-badge ${isAttack ? 'attack-detected' : 'normal-detected'}">
                ${isAttack ? '🚨 THREAT DETECTED' : '✅ TRAFFIC CLEAN'}
            </div>
            <div class="confidence-text">
                Confidence Level: <strong>${result.confidence}%</strong>
            </div>
        `;

        if (result.db_status === 'ok') {
            showToast('✅ Result saved to database!', 'success');
        }

    } catch (e) {
        showToast('Network error: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 ANALYZE TRAFFIC';
    }
}

// ─── Load Analytics ───
async function loadAnalytics() {
    const container = document.getElementById('analyticsCharts');
    try {
        const res = await fetch('/api/history?limit=100');
        const data = await res.json();
        if (data.error || data.length === 0) {
            container.innerHTML = '<p class="no-data-msg">📊 Perform some live scans to see real-time threat analytics here.</p>';
            return;
        }

        const attacks = data.filter(d => d.prediction === 1).length;
        const normal = data.filter(d => d.prediction === 0).length;
        const total = attacks + normal;
        const attackPct = total > 0 ? Math.round((attacks / total) * 100) : 0;
        const normalPct = 100 - attackPct;

        // Build trend bars from probability data
        const trendBars = data.slice(0, 30).reverse().map(d => {
            const prob = (d.probability * 100).toFixed(1);
            const color = d.probability > 0.7 ? '#ef4444' : d.probability > 0.3 ? '#eab308' : '#22c55e';
            return `<div class="trend-bar" style="height:${Math.max(d.probability * 100, 5)}%;background:${color};">
                        <div class="tooltip">${prob}%</div>
                    </div>`;
        }).join('');

        container.innerHTML = `
            <div class="chart-card">
                <h4>Threat Distribution</h4>
                <div class="donut-container">
                    <div class="donut" style="background: conic-gradient(#ef4444 0% ${attackPct}%, #22c55e ${attackPct}% 100%);">
                        <div class="donut-center">${total}</div>
                    </div>
                    <div class="donut-legend">
                        <div><span class="legend-dot" style="background:#22c55e;"></span> Normal: ${normal}</div>
                        <div><span class="legend-dot" style="background:#ef4444;"></span> Attack: ${attacks}</div>
                    </div>
                </div>
            </div>
            <div class="chart-card">
                <h4>Attack Probability Trend (Last ${Math.min(data.length, 30)} scans)</h4>
                <div class="trend-bars">${trendBars}</div>
            </div>
        `;
    } catch (e) {
        container.innerHTML = '<p class="no-data-msg">Failed to load analytics.</p>';
    }
}

// ─── Load History ───
async function loadHistory() {
    const container = document.getElementById('historyTable');
    try {
        const res = await fetch('/api/history?limit=20');
        const data = await res.json();
        if (data.error || data.length === 0) {
            container.innerHTML = '<p class="no-data-msg">No logs found. Perform some scans first!</p>';
            return;
        }

        const rows = data.map(d => {
            const status = d.prediction === 1
                ? '<span class="status-attack">🚨 Attack</span>'
                : '<span class="status-normal">✅ Normal</span>';
            const prob = (d.probability * 100).toFixed(1) + '%';
            const ts = new Date(d.timestamp).toLocaleString();
            return `<tr>
                <td>${ts}</td><td>${status}</td><td>${prob}</td>
                <td>${d.duration}</td><td>${d.src_bytes}</td><td>${d.dst_bytes}</td>
            </tr>`;
        }).join('');

        container.innerHTML = `
            <table class="history-table">
                <thead><tr>
                    <th>Timestamp</th><th>Status</th><th>Probability</th>
                    <th>Duration</th><th>Src Bytes</th><th>Dst Bytes</th>
                </tr></thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    } catch (e) {
        container.innerHTML = '<p class="no-data-msg">Failed to load history.</p>';
    }
}

// ─── Load Models ───
async function loadModels() {
    const container = document.getElementById('modelCards');
    try {
        const res = await fetch('/api/models/metrics');
        const data = await res.json();
        if (data.error || data.length === 0) {
            container.innerHTML = '<p class="no-data-msg">Failed to load model metrics.</p>';
            return;
        }

        const cards = data.map(m => `
            <div class="model-card">
                <h4>${m.name}</h4>
                <div class="metric-row"><span class="metric-label">Accuracy:</span> <span class="metric-value">${(m.accuracy * 100).toFixed(2)}%</span></div>
                <div class="metric-row"><span class="metric-label">Precision:</span> <span class="metric-value">${(m.precision * 100).toFixed(2)}%</span></div>
                <div class="metric-row"><span class="metric-label">Recall:</span> <span class="metric-value">${(m.recall * 100).toFixed(2)}%</span></div>
                <div class="metric-row"><span class="metric-label">F1-Score:</span> <span class="metric-value">${(m.f1 * 100).toFixed(2)}%</span></div>
            </div>
        `).join('');

        container.innerHTML = cards;
    } catch (e) {
        container.innerHTML = '<p class="no-data-msg">Error loading model metrics.</p>';
    }
}

// ─── Toast Notifications ───
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; }, 2500);
    setTimeout(() => toast.remove(), 3000);
}
