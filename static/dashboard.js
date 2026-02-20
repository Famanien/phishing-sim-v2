// Dashboard JavaScript - Handles all interactive functionality

// State management
let currentSection = 'overview';
let templates = [];
let campaigns = [];
let users = [];

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeModals();
    initializeButtons();
    loadDashboardData();
});

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            switchSection(section);
        });
    });
}

function switchSection(section) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${section}"]`).classList.add('active');

    // Update content sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(`${section}-section`).classList.add('active');

    // Update page title
    const titles = {
        'overview': 'Dashboard Overview',
        'campaigns': 'Campaign Management',
        'users': 'Users & Risk Analysis',
        'metrics': 'Performance Metrics',
        'automation': 'Automation & Scheduling',
        'training': 'Phishing Education & Quiz'
    };
    document.getElementById('page-title').textContent = titles[section];

    currentSection = section;

    // Load section-specific data
    loadSectionData(section);
}

// Modal handling
function initializeModals() {
    const modal = document.getElementById('campaign-modal');
    const closeBtn = document.querySelector('.close');
    const cancelBtn = document.getElementById('cancel-campaign');

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });

    // Campaign form submission
    document.getElementById('campaign-form').addEventListener('submit', handleCampaignCreate);
}

// Button handlers
function initializeButtons() {
    document.getElementById('run-weekly-btn').addEventListener('click', handleRunWeekly);
    document.getElementById('create-campaign-btn').addEventListener('click', showCampaignModal);
    document.getElementById('trigger-automation').addEventListener('click', handleRunWeekly);
    document.getElementById('start-quiz-btn').addEventListener('click', startQuiz);
}

// Data loading functions
async function loadDashboardData() {
    await Promise.all([
        loadTemplates(),
        loadDashboardStats(),
        loadCampaigns(),
        loadUsers()
    ]);
}

async function loadSectionData(section) {
    switch (section) {
        case 'overview':
            await loadDashboardStats();
            break;
        case 'campaigns':
            await loadCampaigns();
            break;
        case 'users':
            await loadUsers();
            break;
        case 'metrics':
            await loadMetrics();
            break;
        case 'training':
            // No initial data load needed for training intro, 
            // but we could pre-fetch questions if we wanted.
            break;
    }
}

async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        const data = await response.json();

        if (data.success) {
            templates = data.templates;
            populateTemplateSelect();
        }
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        if (data.success) {
            updateDashboardStats(data.stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadCampaigns() {
    try {
        const response = await fetch('/api/campaigns');
        const data = await response.json();

        if (data.success) {
            campaigns = data.campaigns;
            renderCampaignsTable(data.campaigns);
        }
    } catch (error) {
        console.error('Error loading campaigns:', error);
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();

        if (data.success) {
            users = data.users;
            renderUsersTable(data.users);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function loadMetrics() {
    try {
        const [metricsRes, trendsRes] = await Promise.all([
            fetch('/api/metrics/all'),
            fetch('/api/metrics/trends')
        ]);

        const metricsData = await metricsRes.json();
        const trendsData = await trendsRes.json();

        if (metricsData.success) {
            renderMetricsTable(metricsData.metrics);
        }

        if (trendsData.success && !trendsData.trends.error) {
            renderTrendAnalysis(trendsData.trends);
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
    }
}

// Rendering functions
function updateDashboardStats(stats) {
    document.getElementById('total-users').textContent = stats.total_users;
    document.getElementById('total-campaigns').textContent = stats.total_campaigns;
    document.getElementById('active-campaigns').textContent = stats.active_campaigns;
    document.getElementById('avg-click-rate').textContent = `${stats.average_click_rate}%`;

    // Update risk distribution
    const total = stats.risk_distribution.high + stats.risk_distribution.medium + stats.risk_distribution.low;

    document.getElementById('high-risk-count').textContent = stats.risk_distribution.high;
    document.getElementById('medium-risk-count').textContent = stats.risk_distribution.medium;
    document.getElementById('low-risk-count').textContent = stats.risk_distribution.low;

    if (total > 0) {
        document.getElementById('high-risk-bar').style.width = `${(stats.risk_distribution.high / total) * 100}%`;
        document.getElementById('medium-risk-bar').style.width = `${(stats.risk_distribution.medium / total) * 100}%`;
        document.getElementById('low-risk-bar').style.width = `${(stats.risk_distribution.low / total) * 100}%`;
    }
}

function renderCampaignsTable(campaigns) {
    const tbody = document.getElementById('campaigns-tbody');

    if (campaigns.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No campaigns yet</td></tr>';
        return;
    }

    tbody.innerHTML = campaigns.map(campaign => `
        <tr>
            <td>${campaign.name}</td>
            <td><span class="badge badge-${campaign.difficulty.toLowerCase()}">${campaign.difficulty}</span></td>
            <td><span class="badge badge-${campaign.status}">${campaign.status}</span></td>
            <td>${campaign.target_segment || 'all'}</td>
            <td>${campaign.start_date ? new Date(campaign.start_date).toLocaleDateString() : 'Not set'}</td>
            <td>
                ${campaign.status === 'scheduled' ?
            `<button class="btn btn-secondary" onclick="launchCampaign(${campaign.id})">Launch</button>` :
            campaign.status === 'active' ?
                `<button class="btn btn-secondary" onclick="completeCampaign(${campaign.id})">Complete</button>` :
                '<span class="badge badge-completed">Done</span>'
        }
            </td>
        </tr>
    `).join('');
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-tbody');

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No users yet</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.department || 'N/A'}</td>
            <td>${user.risk_score || 0}</td>
            <td><span class="badge badge-${(user.risk_category || 'low').toLowerCase()}">${user.risk_category || 'Low'}</span></td>
            <td>${user.is_repeat_offender ? '🔴 Yes' : '🟢 No'}</td>
        </tr>
    `).join('');
}

function renderMetricsTable(metrics) {
    const tbody = document.getElementById('metrics-tbody');

    if (metrics.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No metrics available</td></tr>';
        return;
    }

    tbody.innerHTML = metrics.map(m => `
        <tr>
            <td>${m.campaign}</td>
            <td><span class="badge badge-${m.difficulty.toLowerCase()}">${m.difficulty}</span></td>
            <td><span class="badge badge-${m.status}">${m.status}</span></td>
            <td>${m.sent}</td>
            <td>${m.click_rate}</td>
            <td>${m.report_rate}</td>
            <td>${m.training_completion}</td>
        </tr>
    `).join('');
}

function renderTrendAnalysis(trends) {
    const trendCard = document.getElementById('trend-card');
    const trendContent = document.getElementById('trend-content');

    trendCard.style.display = 'block';

    trendContent.innerHTML = `
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
        </div>
        <div style="margin-top: 1.5rem; padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius);">
            <h3>Improvement</h3>
            <p>Click Rate Change: <strong style="color: ${trends.improvement.click_rate_change > 0 ? 'var(--success)' : 'var(--danger)'}">
                ${trends.improvement.click_rate_change > 0 ? '↓' : '↑'} ${Math.abs(trends.improvement.click_rate_change)}%
            </strong></p>
            <p>Report Rate Change: <strong style="color: ${trends.improvement.report_rate_change > 0 ? 'var(--success)' : 'var(--danger)'}">
                ${trends.improvement.report_rate_change > 0 ? '↑' : '↓'} ${Math.abs(trends.improvement.report_rate_change)}%
            </strong></p>
        </div>
    `;
}

function populateTemplateSelect() {
    const select = document.getElementById('campaign-template');
    select.innerHTML = '<option value="">Select a template...</option>' +
        templates.map(t => `<option value="${t.id}">${t.name} (${t.difficulty})</option>`).join('');
}

// Action handlers
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
        const response = await fetch('/api/campaigns/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('campaign-modal').classList.remove('active');
            document.getElementById('campaign-form').reset();
            await loadCampaigns();
            showNotification('Campaign created successfully!', 'success');
        }
    } catch (error) {
        console.error('Error creating campaign:', error);
        showNotification('Error creating campaign', 'error');
    }
}

async function launchCampaign(campaignId) {
    try {
        const response = await fetch(`/api/campaigns/${campaignId}/launch`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            await loadCampaigns();
            await loadDashboardStats();
            showNotification(`Campaign launched! ${data.messages_sent} messages sent.`, 'success');
        } else {
            showNotification(data.error || 'Error launching campaign', 'error');
        }
    } catch (error) {
        console.error('Error launching campaign:', error);
        showNotification('Error launching campaign', 'error');
    }
}

async function completeCampaign(campaignId) {
    try {
        const response = await fetch(`/api/campaigns/${campaignId}/complete`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            await loadCampaigns();
            showNotification('Campaign marked as completed', 'success');
        }
    } catch (error) {
        console.error('Error completing campaign:', error);
        showNotification('Error completing campaign', 'error');
    }
}

async function handleRunWeekly() {
    const weekNumber = parseInt(document.getElementById('week-number').value);

    try {
        const response = await fetch('/api/automation/run-weekly', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ week_number: weekNumber })
        });

        const data = await response.json();

        if (data.success) {
            displayAutomationResults(data);
            await loadDashboardData();
            showNotification(`Week ${weekNumber} simulation completed!`, 'success');
        } else {
            showNotification(data.error || 'Error running simulation', 'error');
        }
    } catch (error) {
        console.error('Error running weekly simulation:', error);
        showNotification('Error running simulation', 'error');
    }
}

function displayAutomationResults(data) {
    const container = document.getElementById('automation-results');

    const html = `
        <div class="result-item">
            <h3>Week ${data.week} Simulation Results</h3>
            <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
            <p><strong>Campaigns Launched:</strong> ${data.campaigns_launched.length}</p>
            <p><strong>Total Messages Sent:</strong> ${data.total_messages}</p>
            
            <div style="margin-top: 1rem;">
                <h4>Campaign Details:</h4>
                ${data.campaigns_launched.map(c => `
                    <div style="margin-top: 0.5rem; padding: 0.5rem; background: var(--bg-secondary); border-radius: 8px;">
                        <p><strong>${c.campaign_name}</strong></p>
                        <p>Messages: ${c.messages_sent} | Target Users: ${c.target_users}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    container.innerHTML = html + container.innerHTML;
}

function showNotification(message, type) {
    // Simple notification - could be enhanced with a toast library
    alert(message);
}

// Make functions globally available
window.launchCampaign = launchCampaign;
window.completeCampaign = completeCampaign;


// --- Quiz / Training Logic ---

let quizQuestions = [];
let currentQuestionIndex = 0;
let quizScore = 0;
let quizUserId = 1; // Default for demo

async function loadQuizQuestions() {
    try {
        const response = await fetch('/api/quiz/questions');
        const data = await response.json();
        if (data.success) {
            quizQuestions = data.questions;
        }
    } catch (error) {
        console.error('Error fetching questions:', error);
        showNotification('Error loading quiz questions', 'error');
    }
}

function startQuiz() {
    currentQuestionIndex = 0;
    quizScore = 0;

    if (quizQuestions.length === 0) {
        loadQuizQuestions().then(() => {
            if (quizQuestions.length > 0) {
                showQuestionUI();
            } else {
                showNotification('No questions available', 'error');
            }
        });
    } else {
        showQuestionUI();
    }
}

function showQuestionUI() {
    document.getElementById('intro-area').style.display = 'none';
    document.getElementById('results-area').style.display = 'none';
    document.getElementById('question-area').style.display = 'block';
    renderQuestion();
}

function renderQuestion() {
    const question = quizQuestions[currentQuestionIndex];
    if (!question) return;

    const questionArea = document.getElementById('question-area');

    const questionHtml = `
        <div class="quiz-progress">
            <div class="progress-info">
                <span>Question ${currentQuestionIndex + 1} of ${quizQuestions.length}</span>
                <span>Score: ${quizScore}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${((currentQuestionIndex + 1) / quizQuestions.length) * 100}%"></div>
            </div>
        </div>
        
        <div class="question-card">
            <div class="category-badge">${question.category}</div>
            <h2>${question.question}</h2>
            
            <div class="options-list">
                ${Object.entries(question.options).map(([key, value]) => `
                    <button class="option-btn" onclick="handleQuizAnswer('${key}', this)">
                        <span class="option-key">${key}</span>
                        <span class="option-text">${value}</span>
                    </button>
                `).join('')}
            </div>
            
            <div id="explanation-area" class="explanation-card" style="display: none;">
                <div class="feedback-icon" id="feedback-icon"></div>
                <div class="explanation-content">
                    <h3 id="feedback-title"></h3>
                    <p id="explanation-text"></p>
                </div>
                <button class="btn btn-primary" id="next-question-btn" onclick="nextQuestion()">Next Question →</button>
            </div>
        </div>
    `;

    questionArea.innerHTML = questionHtml;
}

async function handleQuizAnswer(selectedKey, btn) {
    // Disable all buttons
    const optionBtns = document.querySelectorAll('.option-btn');
    optionBtns.forEach(b => {
        b.disabled = true;
        b.onclick = null;
    });

    const question = quizQuestions[currentQuestionIndex];

    try {
        const response = await fetch('/api/quiz/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: quizUserId,
                question_id: question.id,
                selected_answer: selectedKey
            })
        });

        const data = await response.json();

        if (data.success) {
            const result = data.result;
            const explanationArea = document.getElementById('explanation-area');
            const feedbackIcon = document.getElementById('feedback-icon');
            const feedbackTitle = document.getElementById('feedback-title');
            const explanationText = document.getElementById('explanation-text');

            explanationArea.style.display = 'flex';
            explanationText.textContent = result.explanation;

            if (result.is_correct) {
                btn.classList.add('correct');
                feedbackIcon.innerHTML = '✅';
                feedbackTitle.textContent = 'Correct!';
                feedbackTitle.className = 'correct-text';
                quizScore++;
            } else {
                btn.classList.add('wrong');
                feedbackIcon.innerHTML = '❌';
                feedbackTitle.textContent = 'Incorrect';
                feedbackTitle.className = 'wrong-text';

                // Highlight the correct answer
                optionBtns.forEach(b => {
                    // Extract the key from the HTML or check a data attribute if we added one (we didn't add data-key in onclick version easily)
                    // Let's use the text content set in option-key span
                    const keySpan = b.querySelector('.option-key');
                    if (keySpan && keySpan.textContent === result.correct_answer) {
                        b.classList.add('correct');
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error submitting answer:', error);
        showNotification('Error submitting answer', 'error');
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < quizQuestions.length) {
        renderQuestion();
    } else {
        showQuizResults();
    }
}

function showQuizResults() {
    document.getElementById('question-area').style.display = 'none';
    const resultsArea = document.getElementById('results-area');
    resultsArea.style.display = 'block';

    const percentage = Math.round((quizScore / quizQuestions.length) * 100);
    let message = '';
    let icon = '';

    if (percentage >= 80) {
        message = "Excellent! You're a Phishing Expert!";
        icon = '🏆';
    } else if (percentage >= 60) {
        message = "Good job! You have a solid understanding of email security.";
        icon = '👍';
    } else {
        message = "Keep practicing! Review the explanations to stay safe.";
        icon = '📚';
    }

    resultsArea.innerHTML = `
        <div class="results-card">
            <div class="results-icon">${icon}</div>
            <h1>Quiz Completed!</h1>
            <div class="score-display">
                <span class="score-num">${quizScore} / ${quizQuestions.length}</span>
                <span class="score-percent">(${percentage}%)</span>
            </div>
            <p class="results-message">${message}</p>
            <div class="results-actions">
                <button class="btn btn-primary" onclick="startQuiz()">Retry Quiz</button>
                <button class="btn btn-secondary" onclick="switchSection('overview')">Return to Overview</button>
            </div>
        </div>
    `;
}

// Ensure global access for onclick handlers
window.handleQuizAnswer = handleQuizAnswer;
window.nextQuestion = nextQuestion;
window.startQuiz = startQuiz;
window.switchSection = switchSection; // Re-export just in case
