// ============================================================
// PhishSim Dashboard JS  –  v7.0 Sprint 7
// ============================================================

// ── State ────────────────────────────────────────────────────
let currentSection = 'overview';
let templates = [];
let campaigns = [];
let users = [];
let _trendsData = [];
let _offendersData = [];
let _trendsSortCol = null;
let _trendsSortAsc = true;
let _dateFilterN = 0;   // 0 = all
let _activeRiskFilter = 'all';

// Chart instances (Chart.js)
let _clickRateChart = null;
let _riskDonutChart = null;
let _deptBarChart = null;
let _difficultyChart = null;

// ── Boot ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initializeNavigation();
    initializeModals();
    initializeButtons();
    loadDashboardData();

    // Auto-open section if redirected from phishing reveal page
    const openSection = sessionStorage.getItem('phishsim_open_section');
    if (openSection) {
        sessionStorage.removeItem('phishsim_open_section');
        setTimeout(() => switchSection(openSection), 400);
    }
});

// ── Sidebar collapse ─────────────────────────────────────────
function initSidebar() {
    const toggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main-content');
    if (!toggle) return;
    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        main.classList.toggle('expanded');
        toggle.textContent = sidebar.classList.contains('collapsed') ? '▶' : '◀';
    });
}

// ── Navigation ───────────────────────────────────────────────
function initializeNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            const section = item.dataset.section;
            if (section) switchSection(section);
        });
    });
}

function switchSection(section) {
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    const navEl = document.querySelector(`[data-section="${section}"]`);
    if (navEl) navEl.classList.add('active');

    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
    const secEl = document.getElementById(`${section}-section`);
    if (secEl) secEl.classList.add('active');

    const titles = {
        overview: 'Dashboard Overview',
        campaigns: 'Campaign Management',
        users: 'Users & Risk Analysis',
        metrics: 'Performance Metrics',
        automation: 'Automation & Scheduling',
        training: 'Phishing Education & Quiz',
        analytics: 'Analytics & Behaviour Analysis',
        compliance: 'Legal & Ethical Compliance Analysis'
    };
    document.getElementById('page-title').textContent = titles[section] || section;

    // Show/hide export button only on analytics
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) exportBtn.style.display = section === 'analytics' ? 'inline-flex' : 'none';

    currentSection = section;
    loadSectionData(section);
}

// ── Modals ───────────────────────────────────────────────────
function initializeModals() {
    const modal = document.getElementById('campaign-modal');
    const closeBtn = document.querySelector('#campaign-modal .close');
    const cancelBtn = document.getElementById('cancel-campaign');

    const closeModal = () => modal.classList.remove('active');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    window.addEventListener('click', e => { if (e.target === modal) closeModal(); });
    document.getElementById('campaign-form').addEventListener('submit', handleCampaignCreate);
}

// ── Buttons ──────────────────────────────────────────────────
function initializeButtons() {
    document.getElementById('run-weekly-btn').addEventListener('click', handleRunWeekly);
    document.getElementById('create-campaign-btn').addEventListener('click', showCampaignModal);
    document.getElementById('trigger-automation').addEventListener('click', handleRunWeekly);
    document.getElementById('start-quiz-btn').addEventListener('click', startQuiz);
    
    // Compliance Checklist listeners
    const checklistItems = document.querySelectorAll('#compliance-checklist-card input[type="checkbox"]');
    checklistItems.forEach(item => {
        item.addEventListener('change', updateChecklistProgress);
    });
}

// ── Data loading ─────────────────────────────────────────────
async function loadDashboardData() {
    await Promise.all([loadTemplates(), loadDashboardStats(), loadCampaigns(), loadUsers()]);
}

async function loadSectionData(section) {
    if (section === 'overview') { await loadDashboardStats(); }
    if (section === 'campaigns') { await loadCampaigns(); }
    if (section === 'users') { await loadUsers(); }
    if (section === 'metrics') { await loadMetrics(); }
    if (section === 'analytics') { await loadAnalytics(); }
}

async function loadTemplates() {
    try {
        const r = await fetch('/api/templates');
        const d = await r.json();
        if (d.success) { templates = d.templates; populateTemplateSelect(); }
    } catch (e) { console.error('loadTemplates:', e); }
}

async function loadDashboardStats() {
    try {
        const r = await fetch('/api/dashboard/stats');
        const d = await r.json();
        if (d.success) updateDashboardStats(d.stats);
    } catch (e) { console.error('loadDashboardStats:', e); }
}

async function loadCampaigns() {
    try {
        const r = await fetch('/api/campaigns');
        const d = await r.json();
        if (d.success) { campaigns = d.campaigns; renderCampaignsTable(d.campaigns); }
    } catch (e) { console.error('loadCampaigns:', e); }
}

async function loadUsers() {
    try {
        const r = await fetch('/api/users');
        const d = await r.json();
        if (d.success) { users = d.users; renderUsersTable(d.users); }
    } catch (e) { console.error('loadUsers:', e); }
}

async function loadMetrics() {
    try {
        const [mRes, tRes] = await Promise.all([fetch('/api/metrics/all'), fetch('/api/metrics/trends')]);
        const mData = await mRes.json();
        const tData = await tRes.json();
        if (mData.success) renderMetricsTable(mData.metrics);
        if (tData.success && !tData.trends.error) renderTrendAnalysis(tData.trends);
    } catch (e) { console.error('loadMetrics:', e); }
}

// ── Stats update with count-up ────────────────────────────────
function countUp(el, target, suffix = '', duration = 800) {
    const start = performance.now();
    const from = parseInt(el.textContent) || 0;
    const step = ts => {
        const progress = Math.min((ts - start) / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(from + (target - from) * ease) + suffix;
        if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

function updateDashboardStats(stats) {
    countUp(document.getElementById('total-users'), stats.total_users);
    countUp(document.getElementById('total-campaigns'), stats.total_campaigns);
    countUp(document.getElementById('active-campaigns'), stats.active_campaigns);
    countUp(document.getElementById('avg-click-rate'), stats.average_click_rate, '%');

    // Security Score: higher report rate & lower click rate = better
    const score = Math.round(Math.max(0, Math.min(100,
        100 - (stats.average_click_rate * 1.5) + (stats.average_report_rate * 0.5)
    )));
    const scoreEl = document.getElementById('security-score');
    if (scoreEl) {
        countUp(scoreEl, score, '/100');
        scoreEl.style.color = score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--danger)';
    }

    // Risk bars
    const total = stats.risk_distribution.high + stats.risk_distribution.medium + stats.risk_distribution.low || 1;
    document.getElementById('high-risk-count').textContent = stats.risk_distribution.high;
    document.getElementById('medium-risk-count').textContent = stats.risk_distribution.medium;
    document.getElementById('low-risk-count').textContent = stats.risk_distribution.low;
    document.getElementById('high-risk-bar').style.width = `${(stats.risk_distribution.high / total) * 100}%`;
    document.getElementById('medium-risk-bar').style.width = `${(stats.risk_distribution.medium / total) * 100}%`;
    document.getElementById('low-risk-bar').style.width = `${(stats.risk_distribution.low / total) * 100}%`;

    // Recent activity feed
    const actDiv = document.getElementById('recent-activity');
    const stored = JSON.parse(localStorage.getItem('phishsim_activity') || '[]');
    if (stored.length > 0) {
        actDiv.innerHTML = stored.slice(0, 6).map(a => `
            <div class="activity-item">
                <span class="activity-badge">${a.icon}</span>
                <div>
                    <div class="activity-text">${a.text}</div>
                    <div class="activity-time">${a.time}</div>
                </div>
            </div>`).join('');
    } else {
        actDiv.innerHTML = '<p class="empty-state">No recent activity — run a simulation to get started</p>';
    }
}

// ── Campaigns Table ───────────────────────────────────────────
function renderCampaignsTable(data) {
    const tbody = document.getElementById('campaigns-tbody');
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No campaigns yet – create one to get started!</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(c => `
        <tr data-name="${c.name.toLowerCase()}" data-status="${c.status.toLowerCase()}" data-diff="${(c.difficulty || '').toLowerCase()}">
            <td><strong>${c.name}</strong></td>
            <td><span class="badge badge-${c.difficulty.toLowerCase()}">${c.difficulty}</span></td>
            <td><span class="badge badge-${c.status}">${c.status}</span></td>
            <td>${c.target_segment || 'all'}</td>
            <td>${c.start_date ? new Date(c.start_date).toLocaleDateString() : 'Not set'}</td>
            <td>
                ${c.status === 'scheduled'
            ? `<button class="btn btn-secondary" onclick="confirmLaunch(${c.id})">🚀 Launch</button>`
            : c.status === 'active'
                ? `<button class="btn btn-secondary" onclick="confirmComplete(${c.id})">✅ Complete</button>`
                : '<span class="badge badge-completed">Done</span>'
        }
            </td>
        </tr>`).join('');
    updateCampaignCount();
}

function filterCampaigns() {
    const q = (document.getElementById('campaign-search')?.value || '').trim().toLowerCase();
    const st = document.getElementById('campaign-status-filter')?.value || 'all';
    const diff = document.getElementById('campaign-diff-filter')?.value || 'all';
    let vis = 0;
    document.querySelectorAll('#campaigns-tbody tr[data-name]').forEach(row => {
        const nameMatch = !q || row.dataset.name.includes(q);
        const statMatch = st === 'all' || row.dataset.status === st;
        const diffMatch = diff === 'all' || row.dataset.diff === diff;
        row.style.display = (nameMatch && statMatch && diffMatch) ? '' : 'none';
        if (nameMatch && statMatch && diffMatch) vis++;
    });
    document.getElementById('campaigns-count').textContent = q || st !== 'all' || diff !== 'all'
        ? `Showing ${vis} of ${campaigns.length} campaigns`
        : `${campaigns.length} campaigns total`;
}

function updateCampaignCount() {
    const el = document.getElementById('campaigns-count');
    if (el) el.textContent = `${campaigns.length} campaigns total`;
}

// ── Users Table ───────────────────────────────────────────────
function renderUsersTable(data) {
    const tbody = document.getElementById('users-tbody');
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No users yet</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(u => {
        const risk = (u.risk_category || 'Low').toLowerCase();
        const isHigh = risk === 'high';
        return `<tr class="${isHigh ? 'row-high-risk' : ''}"
                    data-name="${(u.name || '').toLowerCase()}"
                    data-email="${(u.email || '').toLowerCase()}"
                    data-dept="${(u.department || '').toLowerCase()}"
                    data-risk="${u.risk_category || 'Low'}">
            <td>${u.name}</td>
            <td>${u.email}</td>
            <td>${u.department || 'N/A'}</td>
            <td>${u.risk_score || 0}</td>
            <td><span class="badge badge-${risk}">${u.risk_category || 'Low'}</span></td>
            <td>${u.is_repeat_offender ? '🔴 Yes' : '🟢 No'}</td>
        </tr>`;
    }).join('');
    document.getElementById('users-count').textContent = `${data.length} users total`;
}

function filterUsers() {
    const q = (document.getElementById('user-search')?.value || '').trim().toLowerCase();
    let vis = 0;
    document.querySelectorAll('#users-tbody tr[data-name]').forEach(row => {
        const textMatch = !q || row.dataset.name.includes(q) || row.dataset.email.includes(q) || row.dataset.dept.includes(q);
        const riskMatch = _activeRiskFilter === 'all' || row.dataset.risk === _activeRiskFilter;
        row.style.display = (textMatch && riskMatch) ? '' : 'none';
        if (textMatch && riskMatch) vis++;
    });
    const total = users.length;
    const el = document.getElementById('users-count');
    if (el) el.textContent = (q || _activeRiskFilter !== 'all') ? `Showing ${vis} of ${total} users` : `${total} users total`;
}

function setRiskFilter(btn) {
    document.querySelectorAll('.risk-chip').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    _activeRiskFilter = btn.dataset.risk;
    filterUsers();
}

// ── Metrics Table ─────────────────────────────────────────────
function renderMetricsTable(metrics) {
    const tbody = document.getElementById('metrics-tbody');
    if (!metrics || metrics.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No metrics available – run campaigns first</td></tr>';
        return;
    }
    tbody.innerHTML = metrics.map(m => `
        <tr>
            <td>${m.campaign}</td>
            <td><span class="badge badge-${m.difficulty.toLowerCase()}">${m.difficulty}</span></td>
            <td><span class="badge badge-${m.status}">${m.status}</span></td>
            <td>${m.sent}</td>
            <td style="color:${parseFloat(m.click_rate) > 20 ? 'var(--danger)' : 'var(--success)'}"><strong>${m.click_rate}</strong></td>
            <td style="color:${parseFloat(m.report_rate) > 5 ? 'var(--success)' : 'var(--warning)'}"><strong>${m.report_rate}</strong></td>
            <td>${m.training_completion}</td>
        </tr>`).join('');
}

function renderTrendAnalysis(trends) {
    document.getElementById('trend-card').style.display = 'block';
    document.getElementById('trend-content').innerHTML = `
        <div class="two-col-grid">
            <div>
                <h3>Baseline (${trends.baseline.campaign})</h3>
                <p>Click Rate: <strong>${trends.baseline.click_rate}%</strong></p>
                <p>Report Rate: <strong>${trends.baseline.report_rate}%</strong></p>
                <p>Date: ${new Date(trends.baseline.date).toLocaleDateString()}</p>
            </div>
            <div>
                <h3>Latest (${trends.latest.campaign})</h3>
                <p>Click Rate: <strong>${trends.latest.click_rate}%</strong></p>
                <p>Report Rate: <strong>${trends.latest.report_rate}%</strong></p>
                <p>Date: ${new Date(trends.latest.date).toLocaleDateString()}</p>
            </div>
        </div>`;
}

function populateTemplateSelect() {
    const sel = document.getElementById('campaign-template');
    sel.innerHTML = '<option value="">Select a template...</option>' +
        templates.map(t => `<option value="${t.id}">${t.name} (${t.difficulty})</option>`).join('');
}

// ── Actions ───────────────────────────────────────────────────
function showCampaignModal() {
    document.getElementById('campaign-modal').classList.add('active');
}

async function handleCampaignCreate(e) {
    e.preventDefault();
    const formData = {
        name: document.getElementById('campaign-name').value,
        difficulty: document.getElementById('campaign-difficulty').value,
        template_id: parseInt(document.getElementById('campaign-template').value),
        target_segment: document.getElementById('campaign-segment').value,
        start_date: new Date().toISOString()
    };
    try {
        const r = await fetch('/api/campaigns/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        const d = await r.json();
        if (d.success) {
            document.getElementById('campaign-modal').classList.remove('active');
            document.getElementById('campaign-form').reset();
            await loadCampaigns();
            pushActivity('🚀', `Campaign <strong>${formData.name}</strong> created`);
            showToast('Campaign created!', `"${formData.name}" is ready to launch.`, 'success');
        }
    } catch (err) {
        showToast('Error', 'Could not create campaign.', 'error');
    }
}

// Confirm dialogs (replace browser confirm())
function confirmLaunch(id) {
    showConfirm('Launch Campaign', 'This will send phishing emails to the target group. Continue?', 'Launch', 'var(--success)', () => launchCampaign(id));
}

function confirmComplete(id) {
    showConfirm('Complete Campaign', 'Mark this campaign as completed?', 'Complete', 'var(--primary)', () => completeCampaign(id));
}

function showConfirm(title, msg, okLabel, okColor, onOk) {
    const overlay = document.createElement('div');
    overlay.className = 'confirm-modal-overlay';
    overlay.innerHTML = `
        <div class="confirm-modal-box">
            <h3>${title}</h3>
            <p>${msg}</p>
            <div class="confirm-modal-actions">
                <button class="btn btn-secondary" id="_conf-cancel">Cancel</button>
                <button class="btn btn-primary" id="_conf-ok" style="background:${okColor};">${okLabel}</button>
            </div>
        </div>`;
    document.body.appendChild(overlay);
    overlay.querySelector('#_conf-cancel').onclick = () => overlay.remove();
    overlay.querySelector('#_conf-ok').onclick = () => { overlay.remove(); onOk(); };
    overlay.onclick = e => { if (e.target === overlay) overlay.remove(); };
}

async function launchCampaign(id) {
    try {
        const r = await fetch(`/api/campaigns/${id}/launch`, { method: 'POST' });
        const d = await r.json();
        if (d.success) {
            await loadCampaigns();
            await loadDashboardStats();
            pushActivity('📧', `Campaign launched — ${d.messages_sent} messages sent`);
            showToast('Campaign Launched!', `${d.messages_sent} phishing messages sent.`, 'success');
        } else {
            showToast('Launch Failed', d.error || 'Unknown error', 'error');
        }
    } catch (e) { showToast('Error', 'Could not launch campaign.', 'error'); }
}

async function completeCampaign(id) {
    try {
        const r = await fetch(`/api/campaigns/${id}/complete`, { method: 'POST' });
        const d = await r.json();
        if (d.success) {
            await loadCampaigns();
            pushActivity('✅', 'Campaign marked as completed');
            showToast('Campaign Completed', 'The campaign has been closed.', 'info');
        }
    } catch (e) { showToast('Error', 'Could not complete campaign.', 'error'); }
}

async function handleRunWeekly() {
    const week = parseInt(document.getElementById('week-number').value);
    showToast('Running…', `Launching week ${week} simulation, please wait.`, 'info');
    try {
        const r = await fetch('/api/automation/run-weekly', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ week_number: week })
        });
        const d = await r.json();
        if (d.success) {
            displayAutomationResults(d);
            await loadDashboardData();
            pushActivity('⚙️', `Week ${week} simulation completed — ${d.total_messages} messages sent`);
            showToast('Simulation Complete!', `Week ${week} done. ${d.total_messages} messages sent.`, 'success');
        } else {
            showToast('Simulation Failed', d.error || 'Unknown error', 'error');
        }
    } catch (e) { showToast('Error', 'Could not run simulation.', 'error'); }
}

function displayAutomationResults(data) {
    const container = document.getElementById('automation-results');
    const html = `
        <div class="result-item">
            <h3>Week ${data.week} Simulation Results</h3>
            <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
            <p><strong>Campaigns Launched:</strong> ${data.campaigns_launched.length}</p>
            <p><strong>Total Messages Sent:</strong> ${data.total_messages}</p>
            <div style="margin-top:1rem;">
                <h4>Campaign Details:</h4>
                ${data.campaigns_launched.map(c => `
                    <div style="margin-top:.5rem;padding:.5rem;background:var(--bg-secondary);border-radius:8px;">
                        <p><strong>${c.campaign_name}</strong></p>
                        <p>Messages: ${c.messages_sent} | Target Users: ${c.target_users}</p>
                    </div>`).join('')}
            </div>
        </div>`;
    container.innerHTML = html + container.innerHTML;
}

// ── Activity log (localStorage) ────────────────────────────────
function pushActivity(icon, text) {
    const stored = JSON.parse(localStorage.getItem('phishsim_activity') || '[]');
    stored.unshift({ icon, text, time: new Date().toLocaleTimeString() });
    localStorage.setItem('phishsim_activity', JSON.stringify(stored.slice(0, 20)));
}

// ── Toast Notification System ─────────────────────────────────
function showToast(title, message, type = 'info', duration = 4000) {
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || 'ℹ️'}</div>
        <div class="toast-body">
            <div class="toast-title">${title}</div>
            <div class="toast-msg">${message}</div>
        </div>
        <button class="toast-close" onclick="dismissToast(this.parentElement)">×</button>`;
    container.appendChild(toast);
    setTimeout(() => dismissToast(toast), duration);
}

function dismissToast(toast) {
    if (!toast || toast.classList.contains('hiding')) return;
    toast.classList.add('hiding');
    setTimeout(() => toast.remove(), 320);
}

// ── Notification alias (backwards compat) ────────────────────
function showNotification(msg, type) { showToast(type === 'error' ? 'Error' : 'Notice', msg, type); }


// ============================================================
// Quiz / Training Logic
// ============================================================
let quizQuestions = [];
let currentQuestionIndex = 0;
let quizScore = 0;
let quizUserId = 1;

async function loadQuizQuestions() {
    try {
        const r = await fetch('/api/quiz/questions');
        const d = await r.json();
        if (d.success) quizQuestions = d.questions;
    } catch (e) { showToast('Error', 'Could not load quiz questions.', 'error'); }
}

function startQuiz() {
    currentQuestionIndex = 0;
    quizScore = 0;
    if (quizQuestions.length === 0) {
        loadQuizQuestions().then(() => {
            if (quizQuestions.length > 0) showQuestionUI();
            else showToast('No Questions', 'No quiz questions available.', 'error');
        });
    } else { showQuestionUI(); }
}

function showQuestionUI() {
    document.getElementById('intro-area').style.display = 'none';
    document.getElementById('results-area').style.display = 'none';
    document.getElementById('question-area').style.display = 'block';
    renderQuestion();
}

function renderQuestion() {
    const q = quizQuestions[currentQuestionIndex];
    if (!q) return;
    const pct = ((currentQuestionIndex + 1) / quizQuestions.length) * 100;
    document.getElementById('question-area').innerHTML = `
        <div class="quiz-progress">
            <div class="progress-info">
                <span>Question ${currentQuestionIndex + 1} of ${quizQuestions.length}</span>
                <span>Score: ${quizScore}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width:${pct}%"></div>
            </div>
        </div>
        <div class="question-card">
            <div class="category-badge">${q.category}</div>
            <h2>${q.question}</h2>
            <div class="options-list">
                ${Object.entries(q.options).map(([k, v]) => `
                    <button class="option-btn" onclick="handleQuizAnswer('${k}', this)">
                        <span class="option-key">${k}</span>
                        <span class="option-text">${v}</span>
                    </button>`).join('')}
            </div>
            <div id="explanation-area" class="explanation-card" style="display:none;">
                <div class="feedback-icon" id="feedback-icon"></div>
                <div class="explanation-content">
                    <h3 id="feedback-title"></h3>
                    <p id="explanation-text"></p>
                </div>
                <button class="btn btn-primary" onclick="nextQuestion()">Next Question →</button>
            </div>
        </div>`;
}

async function handleQuizAnswer(selectedKey, btn) {
    document.querySelectorAll('.option-btn').forEach(b => { b.disabled = true; b.onclick = null; });
    const q = quizQuestions[currentQuestionIndex];
    try {
        const r = await fetch('/api/quiz/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: quizUserId, question_id: q.id, selected_answer: selectedKey })
        });
        const d = await r.json();
        if (d.success) {
            const result = d.result;
            document.getElementById('explanation-area').style.display = 'flex';
            document.getElementById('explanation-text').textContent = result.explanation;
            if (result.is_correct) {
                btn.classList.add('correct');
                document.getElementById('feedback-icon').innerHTML = '✅';
                document.getElementById('feedback-title').textContent = 'Correct!';
                document.getElementById('feedback-title').className = 'correct-text';
                quizScore++;
            } else {
                btn.classList.add('wrong');
                document.getElementById('feedback-icon').innerHTML = '❌';
                document.getElementById('feedback-title').textContent = 'Incorrect';
                document.getElementById('feedback-title').className = 'wrong-text';
                document.querySelectorAll('.option-btn').forEach(b => {
                    if (b.querySelector('.option-key')?.textContent === result.correct_answer) b.classList.add('correct');
                });
            }
        }
    } catch (e) { showToast('Error', 'Could not submit answer.', 'error'); }
}

function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < quizQuestions.length) renderQuestion();
    else showQuizResults();
}

function showQuizResults() {
    document.getElementById('question-area').style.display = 'none';
    const pct = Math.round((quizScore / quizQuestions.length) * 100);
    let msg = '', icon = '';
    if (pct >= 80) { msg = "Excellent! You're a Phishing Expert!"; icon = '🏆'; }
    else if (pct >= 60) { msg = 'Good job! Solid understanding of email security.'; icon = '👍'; }
    else { msg = 'Keep practicing! Review the explanations to stay safe.'; icon = '📚'; }

    document.getElementById('results-area').style.display = 'block';
    document.getElementById('results-area').innerHTML = `
        <div class="results-card">
            <div class="results-icon">${icon}</div>
            <h1>Quiz Completed!</h1>
            <div class="score-display">
                <span class="score-num">${quizScore} / ${quizQuestions.length}</span>
                <span class="score-percent">(${pct}%)</span>
            </div>
            <p class="results-message">${msg}</p>
            <div class="results-actions">
                <button class="btn btn-primary" onclick="startQuiz()">Retry Quiz</button>
                <button class="btn btn-secondary" onclick="switchSection('overview')">Return to Overview</button>
            </div>
        </div>`;
    pushActivity('🎓', `Quiz completed — scored ${pct}%`);
}


// ============================================================
// Analytics – Sprint 7
// ============================================================

async function loadAnalytics() {
    try {
        const [kpiRes, trendRes, offRes, insRes, riskRes, impRes, riskMetRes] = await Promise.all([
            fetch('/api/analytics/kpis'),
            fetch('/api/analytics/behaviour-trends'),
            fetch('/api/analytics/repeat-offenders'),
            fetch('/api/analytics/pattern-insights'),
            fetch('/api/analytics/risk-distribution'),
            fetch('/api/analytics/campaign-improvement'),
            fetch('/api/analytics/metrics-by-risk-group')
        ]);

        const kpi = await kpiRes.json();
        const trend = await trendRes.json();
        const off = await offRes.json();
        const ins = await insRes.json();
        const risk = await riskRes.json();
        const imp = await impRes.json();
        const riskMet = await riskMetRes.json();

        if (kpi.success) renderKPIs(kpi.kpis);
        if (trend.success) { _trendsData = applyDateFilter(trend.trends); renderBehaviourTrends(_trendsData); updateClickRateChart(_trendsData); updateDifficultyChart(_trendsData); }
        if (off.success) { _offendersData = off.offenders; renderRepeatOffenders(_offendersData); }
        if (ins.success) { renderPatternInsights(ins.insights); renderTop3Templates(ins.insights.top_templates); updateDeptBarChart(ins.insights); }
        if (risk.success) { renderRiskDistribution(risk.distribution); updateRiskDonutChart(risk.distribution); }
        if (imp.success) renderCampaignImprovement(imp.improvement);
        if (riskMet.success) renderMetricsByRiskGroup(riskMet.metrics);

        const ts = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const el = document.getElementById('analytics-last-updated');
        if (el) el.textContent = `Last updated: ${ts}`;

    } catch (err) { console.error('Analytics load error:', err); showToast('Error', 'Could not load analytics data.', 'error'); }
}

function refreshAnalytics() {
    const btn = document.getElementById('analytics-refresh-btn');
    if (btn) { btn.textContent = '⏳ Refreshing…'; btn.disabled = true; }
    loadAnalytics().finally(() => {
        if (btn) { btn.textContent = '🔄 Refresh'; btn.disabled = false; }
    });
}

// Date filter
function setDateFilter(btn, n) {
    document.querySelectorAll('.date-pill').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    _dateFilterN = n;
    refreshAnalytics();
}

function applyDateFilter(trends) {
    if (!_dateFilterN || !trends) return trends;
    return trends.slice(-_dateFilterN);
}

// ── KPI Cards ─────────────────────────────────────────────────
function renderKPIs(kpis) {
    const s = v => (v !== null && v !== undefined) ? v : '—';
    document.getElementById('kpi-click-rate').textContent = `${s(kpis.overall_click_rate)}%`;
    document.getElementById('kpi-report-rate').textContent = `${s(kpis.overall_report_rate)}%`;
    document.getElementById('kpi-training-rate').textContent = `${s(kpis.overall_training_completion)}%`;
    document.getElementById('kpi-repeat-count').textContent = s(kpis.repeat_offender_count);
}

// ── Campaign Improvement Banner ────────────────────────────────
function renderCampaignImprovement(imp) {
    const banner = document.getElementById('improvement-banner');
    if (!banner || !imp || !imp.has_data || imp.campaign_count < 2) { if (banner) banner.style.display = 'none'; return; }
    const arrow = (delta, good) => {
        if (delta === 0) return '<span style="color:var(--text-muted)">→ No change</span>';
        const improved = good ? delta > 0 : delta < 0;
        return `<span style="color:${improved ? 'var(--success)' : 'var(--danger)'};font-weight:700">${improved ? '↑' : '↓'} ${Math.abs(delta)}%</span>`;
    };
    banner.innerHTML = `
        <div class="improvement-header">📊 Programme Progress — <strong>${imp.first.campaign}</strong> → <strong>${imp.latest.campaign}</strong> &nbsp;(${imp.campaign_count} campaigns)</div>
        <div class="improvement-metrics">
            <div class="improvement-metric"><span>Click Rate</span>${arrow(imp.click_delta, false)}</div>
            <div class="improvement-metric"><span>Report Rate</span>${arrow(imp.report_delta, true)}</div>
            <div class="improvement-metric"><span>Training %</span>${arrow(imp.training_delta, true)}</div>
        </div>`;
    banner.style.display = 'block';
}

// ── Risk Distribution bars ─────────────────────────────────────
function renderRiskDistribution(dist) {
    const container = document.getElementById('risk-distribution-chart');
    if (!container) return;
    const total = dist.all_users || 1;
    const bar = (label, count, color, icon) => {
        const pct = total > 0 ? Math.round((count / total) * 100) : 0;
        return `<div class="risk-bar-row">
            <div class="risk-bar-label">${icon} ${label}</div>
            <div class="risk-bar-track"><div class="risk-bar-fill" style="width:${pct}%;background:${color};"></div></div>
            <div class="risk-bar-value">${count} <span style="color:var(--text-muted)">(${pct}%)</span></div>
        </div>`;
    };
    container.innerHTML = `
        <div class="risk-total-label">Total users: <strong>${total}</strong></div>
        ${bar('High Risk', dist.high_count || 0, 'var(--danger)', '🔴')}
        ${bar('Medium Risk', dist.medium_count || 0, 'var(--warning)', '🟡')}
        ${bar('Low Risk', dist.low_count || 0, 'var(--success)', '🟢')}
        ${bar('Unassessed', dist.unassessed || 0, 'var(--text-muted)', '⚪')}`;
}

// ── Behaviour Trends table ────────────────────────────────────
function renderBehaviourTrends(trends) {
    const tbody = document.getElementById('trends-tbody');
    if (!trends || trends.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No campaign data yet – run a simulation first</td></tr>';
        return;
    }
    tbody.innerHTML = trends.map((t, i) => `
        <tr>
            <td>${i + 1}</td>
            <td>${t.campaign}</td>
            <td><span class="badge badge-${(t.difficulty || '').toLowerCase()}">${t.difficulty}</span></td>
            <td>${t.total_sent}</td>
            <td style="color:${t.click_rate > 20 ? 'var(--danger)' : 'var(--success)'};font-weight:600">${t.click_rate}%</td>
            <td style="color:${t.report_rate > 5 ? 'var(--success)' : 'var(--warning)'};font-weight:600">${t.report_rate}%</td>
            <td style="color:${t.training_completion_rate > 60 ? 'var(--success)' : 'var(--warning)'};font-weight:600">${t.training_completion_rate}%</td>
        </tr>`).join('');

    // Observations
    const obs = document.getElementById('trend-observations');
    const observations = [];
    if (trends.length >= 2) {
        const first = trends[0], last = trends[trends.length - 1];
        const cd = (first.click_rate - last.click_rate).toFixed(1);
        const rd = (last.report_rate - first.report_rate).toFixed(1);
        const td = (last.training_completion_rate - first.training_completion_rate).toFixed(1);
        if (cd > 0) observations.push(`✅ Click rate improved by <strong>${cd}%</strong> from first to latest campaign.`);
        else if (cd < 0) observations.push(`⚠️ Click rate increased by <strong>${Math.abs(cd)}%</strong> – harder campaigns may drive short-term spikes.`);
        if (rd > 0) observations.push(`✅ Report rate increased by <strong>${rd}%</strong>, indicating growing security awareness.`);
        if (td > 0) observations.push(`✅ Training completion improved by <strong>${td}%</strong>.`);
        const hard = trends.filter(t => t.difficulty === 'Hard');
        if (hard.length > 0) {
            const avg = (hard.reduce((s, t) => s + t.click_rate, 0) / hard.length).toFixed(1);
            observations.push(`📊 Hard campaigns averaged a <strong>${avg}%</strong> click rate.`);
        }
    } else { observations.push('Run more campaigns to generate trend observations.'); }

    obs.innerHTML = `
        <h3 style="margin-bottom:.75rem;">📝 Observations</h3>
        <ul style="list-style:none;padding:0;">
            ${observations.map(o => `<li style="padding:.5rem 0;border-bottom:1px solid var(--border);">${o}</li>`).join('')}
        </ul>`;
}

// ── Sort Trends ───────────────────────────────────────────────
function sortTrends(col) {
    _trendsSortAsc = (_trendsSortCol === col) ? !_trendsSortAsc : true;
    _trendsSortCol = col;
    const sorted = [..._trendsData].sort((a, b) => {
        const va = a[col] ?? '', vb = b[col] ?? '';
        if (typeof va === 'number') return _trendsSortAsc ? va - vb : vb - va;
        return _trendsSortAsc ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
    });
    document.querySelectorAll('#trends-table th.sortable').forEach(th => {
        th.textContent = th.textContent.replace(/ [▲▼⇅]$/, '') + ' ⇅';
        if (th.dataset.col === col) th.textContent = th.textContent.replace(' ⇅', '') + (_trendsSortAsc ? ' ▲' : ' ▼');
    });
    renderBehaviourTrends(sorted);
}

// ── Repeat Offenders ──────────────────────────────────────────
function renderRepeatOffenders(offenders) {
    const tbody = document.getElementById('offenders-tbody');
    const label = document.getElementById('offender-count-label');
    if (!offenders || offenders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">🟢 No repeat offenders – great news!</td></tr>';
        if (label) label.textContent = '';
        return;
    }
    tbody.innerHTML = offenders.map(o => `
        <tr data-name="${(o.name || '').toLowerCase()}" data-email="${(o.email || '').toLowerCase()}" data-dept="${(o.department || '').toLowerCase()}">
            <td>${o.name}</td>
            <td>${o.email}</td>
            <td>${o.department || 'N/A'}</td>
            <td style="font-weight:700;color:var(--danger);">${o.total_clicks}</td>
            <td>${o.campaigns_clicked}</td>
            <td><span class="badge badge-${(o.risk_category || 'low').toLowerCase()}">${o.risk_category || 'N/A'}</span></td>
            <td>${o.clicked_after_training
            ? '<span style="color:var(--danger);">🔴 Yes</span>'
            : '<span style="color:var(--success);">🟢 No</span>'}</td>
        </tr>`).join('');
    if (label) label.textContent = `Showing ${offenders.length} repeat offender${offenders.length !== 1 ? 's' : ''}`;
}

function filterOffenders(query) {
    const q = (query || '').trim().toLowerCase();
    let vis = 0;
    document.querySelectorAll('#offenders-tbody tr[data-name]').forEach(row => {
        const match = !q || row.dataset.name.includes(q) || row.dataset.email.includes(q) || row.dataset.dept.includes(q);
        row.style.display = match ? '' : 'none';
        if (match) vis++;
    });
    const label = document.getElementById('offender-count-label');
    if (label) label.textContent = q ? `Showing ${vis} of ${_offendersData.length} offenders matching "${query}"`
        : `Showing ${_offendersData.length} repeat offender${_offendersData.length !== 1 ? 's' : ''}`;
}

// ── Pattern Insights ──────────────────────────────────────────
function miniBar(pct, color) {
    return `<div style="display:inline-block;width:60px;height:8px;background:var(--bg-tertiary);border-radius:4px;vertical-align:middle;margin-right:6px;overflow:hidden;">
        <div style="width:${Math.min(pct, 100)}%;height:100%;background:${color};border-radius:4px;"></div>
    </div>`;
}

function renderPatternInsights(insights) {
    const tBody = document.getElementById('template-insights-tbody');
    if (insights.top_templates && insights.top_templates.length > 0) {
        tBody.innerHTML = insights.top_templates.map((t, i) => `
            <tr>
                <td>${i === 0 ? '🥇 ' : i === 1 ? '🥈 ' : i === 2 ? '🥉 ' : ''}${t.template_name}</td>
                <td><span class="badge badge-${(t.difficulty || '').toLowerCase()}">${t.difficulty}</span></td>
                <td>${miniBar(t.click_rate, t.click_rate > 20 ? 'var(--danger)' : 'var(--success)')}<strong style="color:${t.click_rate > 20 ? 'var(--danger)' : 'var(--success)'}">${t.click_rate}%</strong></td>
                <td>${t.total_sent}</td>
            </tr>`).join('');
    } else {
        tBody.innerHTML = '<tr><td colspan="4" class="empty-state">No data yet – run campaigns first</td></tr>';
    }

    const dBody = document.getElementById('dept-insights-tbody');
    if (insights.department_risk && insights.department_risk.length > 0) {
        dBody.innerHTML = insights.department_risk.map(d => {
            const color = d.click_rate > 20 ? 'var(--danger)' : d.click_rate > 10 ? 'var(--warning)' : 'var(--success)';
            return `<tr><td>${d.department}</td><td>${miniBar(d.click_rate, color)}<strong style="color:${color}">${d.click_rate}%</strong></td><td>${d.total_sent}</td></tr>`;
        }).join('');
    } else {
        dBody.innerHTML = '<tr><td colspan="3" class="empty-state">No data yet</td></tr>';
    }
}

// ── Metrics by Risk Group ─────────────────────────────────────
function renderMetricsByRiskGroup(metrics) {
    const tbody = document.getElementById('risk-group-tbody');
    if (!tbody) return;
    if (!metrics || metrics.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No risk data yet – run campaigns first</td></tr>';
        return;
    }
    tbody.innerHTML = metrics.map(m => `
        <tr>
            <td><span class="badge badge-${(m.risk_category || '').toLowerCase()}">${m.risk_category}</span></td>
            <td>${m.user_count}</td>
            <td style="color:${m.avg_click_rate > 20 ? 'var(--danger)' : 'var(--success)'};font-weight:600">${m.avg_click_rate !== null ? m.avg_click_rate + '%' : '—'}</td>
            <td style="color:${m.avg_report_rate > 5 ? 'var(--success)' : 'var(--warning)'};font-weight:600">${m.avg_report_rate !== null ? m.avg_report_rate + '%' : '—'}</td>
            <td style="color:${m.avg_training_rate > 60 ? 'var(--success)' : 'var(--warning)'};font-weight:600">${m.avg_training_rate !== null ? m.avg_training_rate + '%' : '—'}</td>
        </tr>`).join('');
}

// ── Top 3 Riskiest Templates ──────────────────────────────────
function renderTop3Templates(tmplts) {
    const grid = document.getElementById('top3-templates-grid');
    if (!grid) return;
    if (!tmplts || tmplts.length === 0) {
        grid.innerHTML = '<p class="empty-state">No template data yet – run campaigns first</p>';
        return;
    }
    const medals = ['🥇', '🥈', '🥉'];
    const colors = ['var(--danger)', 'var(--warning)', 'var(--text-secondary)'];
    grid.innerHTML = tmplts.slice(0, 3).map((t, i) => `
        <div class="top3-card">
            <div class="top3-medal">${medals[i]}</div>
            <div class="top3-name">${t.template_name}</div>
            <div class="top3-badge"><span class="badge badge-${(t.difficulty || '').toLowerCase()}">${t.difficulty}</span></div>
            <div class="top3-rate" style="color:${colors[i]}">${t.click_rate}%</div>
            <div class="top3-label">click rate</div>
            <div class="top3-sent">${t.total_sent} sent</div>
        </div>`).join('');
}

// ============================================================
// Chart.js Charts
// ============================================================

const CHART_DEFAULTS = {
    color: '#f1f5f9',
    font: { family: 'Inter, sans-serif', size: 12 },
    grid: { color: 'rgba(51,65,85,0.6)' }
};

function chartDefaults(ctx) {
    return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: { labels: { color: CHART_DEFAULTS.color, font: CHART_DEFAULTS.font, padding: 12 } },
            tooltip: {
                backgroundColor: '#1e293b',
                borderColor: '#334155',
                borderWidth: 1,
                titleColor: '#f1f5f9',
                bodyColor: '#cbd5e1',
                padding: 10
            }
        },
        scales: {
            x: { ticks: { color: CHART_DEFAULTS.color, font: CHART_DEFAULTS.font }, grid: CHART_DEFAULTS.grid },
            y: { ticks: { color: CHART_DEFAULTS.color, font: CHART_DEFAULTS.font }, grid: CHART_DEFAULTS.grid, beginAtZero: true }
        }
    };
}

// Click Rate Over Time (line chart)
function updateClickRateChart(trends) {
    const ctx = document.getElementById('click-rate-chart');
    if (!ctx) return;

    const labels = trends.map(t => t.campaign);
    const clickData = trends.map(t => t.click_rate);
    const reportData = trends.map(t => t.report_rate);

    if (_clickRateChart) _clickRateChart.destroy();
    _clickRateChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Click Rate %',
                    data: clickData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239,68,68,0.15)',
                    tension: 0.4,
                    pointBackgroundColor: '#ef4444',
                    pointRadius: 5,
                    fill: true
                },
                {
                    label: 'Report Rate %',
                    data: reportData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16,185,129,0.1)',
                    tension: 0.4,
                    pointBackgroundColor: '#10b981',
                    pointRadius: 5,
                    fill: false
                }
            ]
        },
        options: {
            ...chartDefaults(ctx),
            plugins: {
                ...chartDefaults(ctx).plugins,
                legend: { display: true, labels: { color: CHART_DEFAULTS.color, font: CHART_DEFAULTS.font } }
            }
        }
    });
}

// Risk Donut Chart
function updateRiskDonutChart(dist) {
    const ctx = document.getElementById('risk-donut-chart');
    if (!ctx) return;

    if (_riskDonutChart) _riskDonutChart.destroy();
    _riskDonutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High Risk', 'Medium Risk', 'Low Risk', 'Unassessed'],
            datasets: [{
                data: [dist.high_count || 0, dist.medium_count || 0, dist.low_count || 0, dist.unassessed || 0],
                backgroundColor: ['rgba(239,68,68,0.85)', 'rgba(245,158,11,0.85)', 'rgba(16,185,129,0.85)', 'rgba(148,163,184,0.5)'],
                borderColor: ['#ef4444', '#f59e0b', '#10b981', '#94a3b8'],
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: { position: 'bottom', labels: { color: CHART_DEFAULTS.color, font: CHART_DEFAULTS.font, padding: 10, boxWidth: 14 } },
                tooltip: { backgroundColor: '#1e293b', borderColor: '#334155', borderWidth: 1, titleColor: '#f1f5f9', bodyColor: '#cbd5e1', padding: 10 }
            }
        }
    });
}

// Department Horizontal Bar Chart
function updateDeptBarChart(insights) {
    const ctx = document.getElementById('dept-bar-chart');
    if (!ctx || !insights.department_risk || !insights.department_risk.length) return;

    const labels = insights.department_risk.map(d => d.department);
    const data = insights.department_risk.map(d => d.click_rate);
    const colors = data.map(v => v > 20 ? 'rgba(239,68,68,0.8)' : v > 10 ? 'rgba(245,158,11,0.8)' : 'rgba(16,185,129,0.8)');

    if (_deptBarChart) _deptBarChart.destroy();
    _deptBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Click Rate %',
                data,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            ...chartDefaults(ctx),
            indexAxis: 'y',
            plugins: { ...chartDefaults(ctx).plugins, legend: { display: false } }
        }
    });
}

// Difficulty Grouped Bar Chart
function updateDifficultyChart(trends) {
    const ctx = document.getElementById('difficulty-chart');
    if (!ctx || !trends || !trends.length) return;

    const groups = { Easy: [], Medium: [], Hard: [] };
    trends.forEach(t => { if (groups[t.difficulty]) groups[t.difficulty].push(t.click_rate); });
    const labels = ['Easy', 'Medium', 'Hard'];
    const avgs = labels.map(d => {
        const arr = groups[d];
        return arr.length ? parseFloat((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)) : 0;
    });

    if (_difficultyChart) _difficultyChart.destroy();
    _difficultyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Avg Click Rate %',
                data: avgs,
                backgroundColor: ['rgba(16,185,129,0.75)', 'rgba(245,158,11,0.75)', 'rgba(239,68,68,0.75)'],
                borderColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            ...chartDefaults(ctx),
            plugins: { ...chartDefaults(ctx).plugins, legend: { display: false } }
        }
    });
}

// ── Global exports ────────────────────────────────────────────
window.loadAnalytics = loadAnalytics;
window.refreshAnalytics = refreshAnalytics;
window.filterOffenders = filterOffenders;
window.sortTrends = sortTrends;
window.setDateFilter = setDateFilter;
window.filterCampaigns = filterCampaigns;
window.filterUsers = filterUsers;
window.setRiskFilter = setRiskFilter;
window.launchCampaign = launchCampaign;
window.completeCampaign = completeCampaign;
window.confirmLaunch = confirmLaunch;
window.confirmComplete = confirmComplete;
window.handleQuizAnswer = handleQuizAnswer;
window.nextQuestion = nextQuestion;
window.startQuiz = startQuiz;
window.switchSection = switchSection;
window.showToast = showToast;
window.dismissToast = dismissToast;

// ── Compliance PDF Download ──────────────────────────────────
async function downloadCompliancePDF() {
    const { jsPDF } = window.jspdf;
    const element = document.getElementById('compliance-section');
    if (!element) return;

    showToast('Generating PDF...', 'Please wait while we prepare your document.', 'info');

    try {
        const canvas = await html2canvas(element, {
            scale: 2,
            useCORS: true,
            logging: false,
            backgroundColor: '#0f172a' // Match dashboard background
        });
        
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgProps = pdf.getImageProperties(imgData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
        
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save('PhishSim_Compliance_Analysis.pdf');
        
        showToast('Success!', 'Compliance PDF has been downloaded.', 'success');
    } catch (err) {
        console.error('PDF generation error:', err);
        showToast('Error', 'Failed to generate PDF. Please try again.', 'error');
    }
}
window.downloadCompliancePDF = downloadCompliancePDF;

// ── Compliance Checklist Progress ────────────────────────────
function updateChecklistProgress() {
    const total = document.querySelectorAll('#compliance-checklist-card input[type="checkbox"]').length;
    const checked = document.querySelectorAll('#compliance-checklist-card input[type="checkbox"]:checked').length;
    const pct = Math.round((checked / total) * 100);
    
    const progressEl = document.getElementById('checklist-progress');
    if (progressEl) {
        progressEl.innerHTML = `
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Compliance Readiness</span>
                <span>${checked} of ${total} (${pct}%)</span>
            </div>
            <div class="risk-progress" style="height:8px; background:var(--bg-tertiary);">
                <div class="risk-fill" style="width:${pct}%; background:${pct === 100 ? 'var(--success)' : 'var(--warning)'}; transition: width 0.3s ease;"></div>
            </div>
        `;
    }
}
window.updateChecklistProgress = updateChecklistProgress;
