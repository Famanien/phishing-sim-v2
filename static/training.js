/**
 * Training and Quiz Logic - Educational Section
 */

document.addEventListener('DOMContentLoaded', () => {
    const quizContainer = document.getElementById('quiz-container');
    const startBtn = document.getElementById('start-quiz-btn');
    const questionArea = document.getElementById('question-area');
    const introArea = document.getElementById('intro-area');
    const resultsArea = document.getElementById('results-area');

    let questions = [];
    let currentQuestionIndex = 0;
    let score = 0;
    let userId = 1; // Default for demo, should be dynamic in a real app

    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // If they click on a nav item that isn't training, redirect to dashboard
            if (!item.classList.contains('active')) {
                window.location.href = '/';
            }
        });
    });

    // Start Quiz
    startBtn.addEventListener('click', async () => {
        await fetchQuestions();
        if (questions.length > 0) {
            introArea.style.display = 'none';
            questionArea.style.display = 'block';
            renderQuestion();
        }
    });

    async function fetchQuestions() {
        try {
            const response = await fetch('/api/quiz/questions');
            const data = await response.json();
            if (data.success) {
                questions = data.questions;
            }
        } catch (error) {
            console.error('Error fetching questions:', error);
        }
    }

    function renderQuestion() {
        const question = questions[currentQuestionIndex];
        const questionHtml = `
            <div class="quiz-progress">
                <div class="progress-info">
                    <span>Question ${currentQuestionIndex + 1} of ${questions.length}</span>
                    <span>Score: ${score}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${((currentQuestionIndex + 1) / questions.length) * 100}%"></div>
                </div>
            </div>
            
            <div class="question-card">
                <div class="category-badge">${question.category}</div>
                <h2>${question.question}</h2>
                
                <div class="options-list">
                    ${Object.entries(question.options).map(([key, value]) => `
                        <button class="option-btn" data-key="${key}">
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
                    <button class="btn btn-primary" id="next-btn">Next Question →</button>
                </div>
            </div>
        `;

        questionArea.innerHTML = questionHtml;

        // Add listeners to option buttons
        const optionBtns = questionArea.querySelectorAll('.option-btn');
        optionBtns.forEach(btn => {
            btn.addEventListener('click', () => handleAnswer(btn.dataset.key, btn));
        });
    }

    async function handleAnswer(selectedKey, btn) {
        // Disable all buttons
        const optionBtns = questionArea.querySelectorAll('.option-btn');
        optionBtns.forEach(b => b.disabled = true);

        const question = questions[currentQuestionIndex];

        try {
            const response = await fetch('/api/quiz/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
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
                const nextBtn = document.getElementById('next-btn');

                explanationArea.style.display = 'flex';
                explanationText.textContent = result.explanation;

                if (result.is_correct) {
                    btn.classList.add('correct');
                    feedbackIcon.innerHTML = '✅';
                    feedbackTitle.textContent = 'Correct!';
                    feedbackTitle.className = 'correct-text';
                    score++;
                } else {
                    btn.classList.add('wrong');
                    feedbackIcon.innerHTML = '❌';
                    feedbackTitle.textContent = 'Incorrect';
                    feedbackTitle.className = 'wrong-text';

                    // Highlight the correct answer
                    optionBtns.forEach(b => {
                        if (b.dataset.key === result.correct_answer) {
                            b.classList.add('correct');
                        }
                    });
                }

                nextBtn.addEventListener('click', () => {
                    currentQuestionIndex++;
                    if (currentQuestionIndex < questions.length) {
                        renderQuestion();
                    } else {
                        showResults();
                    }
                });
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    }

    async function showResults() {
        questionArea.style.display = 'none';
        resultsArea.style.display = 'block';

        const percentage = Math.round((score / questions.length) * 100);
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
                    <span class="score-num">${score} / ${questions.length}</span>
                    <span class="score-percent">(${percentage}%)</span>
                </div>
                <p class="results-message">${message}</p>
                <div class="results-actions">
                    <button class="btn btn-primary" onclick="window.location.reload()">Retry Quiz</button>
                    <button class="btn btn-secondary" onclick="window.location.href='/'">Return to Dashboard</button>
                </div>
            </div>
        `;
    }
});
