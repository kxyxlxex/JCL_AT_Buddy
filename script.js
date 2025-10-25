class TestGenerator {
    constructor() {
        this.allQuestions = {};
        this.currentTest = [];
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.timeRemaining = 50 * 60; // 50 minutes in seconds
        this.timer = null;
        
        this.initializeEventListeners();
        this.loadAllQuestions();
    }
    
    initializeEventListeners() {
        // Test selection buttons
        document.querySelectorAll('.test-option').forEach(button => {
            button.addEventListener('click', (e) => {
                const subject = e.currentTarget.dataset.subject;
                this.startTest(subject);
            });
        });
        
        // Test navigation
        document.getElementById('prevQuestion').addEventListener('click', () => this.previousQuestion());
        document.getElementById('nextQuestion').addEventListener('click', () => this.nextQuestion());
        document.getElementById('submitTest').addEventListener('click', () => this.submitTest());
        
        // Results actions
        document.getElementById('reviewAnswers').addEventListener('click', () => this.reviewAnswers());
        document.getElementById('newTest').addEventListener('click', () => this.newTest());
        
        // Review actions
        document.getElementById('backToResults').addEventListener('click', () => this.backToResults());
        document.getElementById('newTestFromReview').addEventListener('click', () => this.newTest());
        
        // Auto-save when page is about to be closed
        window.addEventListener('beforeunload', () => {
            if (this.currentTest && this.currentTest.length > 0) {
                this.saveProgress();
            }
        });
        
        // Auto-save when user switches tabs or minimizes browser
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.currentTest && this.currentTest.length > 0) {
                this.saveProgress();
            }
        });
    }
    
    async loadAllQuestions() {
        try {
            // Load consolidated question files for each subject
            const subjects = [
                'Derivatives_I', 'Derivatives_II',
                'History_of_the_Empire', 'History_of_the_Monarchy_and_Republic',
                'Mottoes_Abbreviations_and_Quotations', 'Mythology', 'Vocabulary_I', 'Vocabulary_II'
            ];
            
            for (const subject of subjects) {
                try {
                    const response = await fetch(`data/${subject}.json`);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.questions) {
                            this.allQuestions[subject] = data.questions;
                            console.log(`Loaded ${data.questions.length} questions for ${subject}`);
                        }
                    } else {
                        console.log(`No data found for ${subject}`);
                        this.allQuestions[subject] = [];
                    }
                } catch (error) {
                    console.log(`Error loading ${subject}:`, error);
                    this.allQuestions[subject] = [];
                }
            }
            
            console.log('All questions loaded:', this.allQuestions);
        } catch (error) {
            console.error('Error loading questions:', error);
        }
    }
    
    startTest(subject) {
        if (!this.allQuestions[subject] || this.allQuestions[subject].length === 0) {
            alert('No questions available for this subject yet. Please try another subject.');
            return;
        }
        
        this.currentSubject = subject;
        
        // Check for saved progress
        const savedProgress = this.loadProgress(subject);
        if (savedProgress) {
            const resume = confirm(`You have a saved test in progress for ${subject.replace(/_/g, ' ')}. Would you like to resume it?`);
            if (resume) {
                this.resumeTest(savedProgress);
                return;
            }
        }
        
        // Hide test selection, show test interface
        document.querySelector('.test-selection').style.display = 'none';
        document.getElementById('testInterface').style.display = 'block';
        document.getElementById('results').style.display = 'none';
        
        // Generate random 50 questions from all years for this subject
        this.generateRandomTest(subject);
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.timeRemaining = 50 * 60;
        
        // Start timer
        this.startTimer();
        
        // Display first question
        this.displayQuestion();
    }
    
    generateRandomTest(subject) {
        const allSubjectQuestions = this.allQuestions[subject];
        const shuffled = [...allSubjectQuestions].sort(() => Math.random() - 0.5);
        this.currentTest = shuffled.slice(0, 50);
        
        // Renumber questions 1-50
        this.currentTest.forEach((question, index) => {
            question.question_number = index + 1;
        });
    }
    
    displayQuestion() {
        const question = this.currentTest[this.currentQuestionIndex];
        
        // Update header
        document.getElementById('questionCounter').textContent = 
            `Question ${this.currentQuestionIndex + 1} of 50`;
        
        // Display question
        document.getElementById('questionText').textContent = question.question;
        
        // Display options
        const optionsContainer = document.getElementById('optionsContainer');
        optionsContainer.innerHTML = '';
        
        Object.entries(question.options).forEach(([key, value]) => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'option';
            
            const radio = document.createElement('input');
            radio.type = 'radio';
            radio.name = 'question';
            radio.value = key;
            radio.id = `option-${key}`;
            
            // Check if user already answered this question
            if (this.userAnswers[this.currentQuestionIndex] === key) {
                radio.checked = true;
                optionDiv.classList.add('selected');
            }
            
            const label = document.createElement('label');
            label.htmlFor = `option-${key}`;
            label.textContent = `${key}. ${value}`;
            
            optionDiv.appendChild(radio);
            optionDiv.appendChild(label);
            optionsContainer.appendChild(optionDiv);
            
            // Add click handler for the entire option div
            optionDiv.addEventListener('click', () => {
                radio.checked = true;
                this.selectAnswer(key);
            });
        });
        
        // Update navigation buttons
        document.getElementById('prevQuestion').disabled = this.currentQuestionIndex === 0;
        document.getElementById('nextQuestion').disabled = this.currentQuestionIndex === 49;
    }
    
    selectAnswer(answer) {
        this.userAnswers[this.currentQuestionIndex] = answer;
        
        // Save progress automatically when user answers a question
        this.saveProgress();
        
        // Update visual selection
        document.querySelectorAll('.option').forEach(option => {
            option.classList.remove('selected');
        });
        document.querySelector(`input[value="${answer}"]`).parentElement.classList.add('selected');
    }
    
    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayQuestion();
            this.saveProgress(); // Save progress when navigating
        }
    }
    
    nextQuestion() {
        if (this.currentQuestionIndex < 49) {
            this.currentQuestionIndex++;
            this.displayQuestion();
            this.saveProgress(); // Save progress when navigating
        }
    }
    
    startTimer() {
        this.timer = setInterval(() => {
            this.timeRemaining--;
            const minutes = Math.floor(this.timeRemaining / 60);
            const seconds = this.timeRemaining % 60;
            document.getElementById('timeRemaining').textContent = 
                `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            // Auto-save every 30 seconds
            if (this.timeRemaining % 30 === 0) {
                this.saveProgress();
            }
            
            if (this.timeRemaining <= 0) {
                this.submitTest();
            }
        }, 1000);
    }
    
    submitTest() {
        clearInterval(this.timer);
        
        // Calculate score
        let correct = 0;
        this.currentTest.forEach((question, index) => {
            if (this.userAnswers[index] === question.correct_answer) {
                correct++;
            }
        });
        
        const percentage = Math.round((correct / 50) * 100);
        
        // Hide test interface, show results
        document.getElementById('testInterface').style.display = 'none';
        document.getElementById('results').style.display = 'block';
        
        // Display results
        document.getElementById('scorePercentage').textContent = `${percentage}%`;
        document.getElementById('scoreText').textContent = `You scored ${correct} out of 50`;
        
        // Store results for review
        this.testResults = {
            questions: this.currentTest,
            userAnswers: this.userAnswers,
            score: correct,
            percentage: percentage
        };
        
        // Clear saved progress since test is completed
        this.clearProgress();
    }
    
    reviewAnswers() {
        // Hide results, show detailed review
        document.getElementById('results').style.display = 'none';
        document.getElementById('reviewInterface').style.display = 'block';
        
        const reviewContainer = document.getElementById('reviewContainer');
        reviewContainer.innerHTML = '';
        
        this.currentTest.forEach((question, index) => {
            const userAnswer = this.userAnswers[index];
            const correctAnswer = question.correct_answer;
            const isCorrect = userAnswer === correctAnswer;
            
            const questionDiv = document.createElement('div');
            questionDiv.className = `review-question ${isCorrect ? 'correct' : 'incorrect'}`;
            
            questionDiv.innerHTML = `
                <div class="question-header">
                    <h4>Question ${index + 1} ${isCorrect ? '✓' : '✗'}</h4>
                    <span class="status ${isCorrect ? 'correct' : 'incorrect'}">
                        ${isCorrect ? 'Correct' : 'Incorrect'}
                    </span>
                </div>
                <div class="question-text">${question.question}</div>
                <div class="options-review">
                    ${Object.entries(question.options).map(([key, value]) => `
                        <div class="option-review ${key === correctAnswer ? 'correct-answer' : ''} ${key === userAnswer && !isCorrect ? 'user-answer-wrong' : ''}">
                            <span class="option-letter">${key}.</span>
                            <span class="option-text">${value}</span>
                            ${key === correctAnswer ? '<span class="correct-label">✓ Correct Answer</span>' : ''}
                            ${key === userAnswer && !isCorrect ? '<span class="user-label">Your Answer</span>' : ''}
                        </div>
                    `).join('')}
                </div>
            `;
            
            reviewContainer.appendChild(questionDiv);
        });
    }
    
    backToResults() {
        // Hide review, show results
        document.getElementById('reviewInterface').style.display = 'none';
        document.getElementById('results').style.display = 'block';
    }
    
    newTest() {
        // Reset everything and go back to test selection
        document.getElementById('results').style.display = 'none';
        document.getElementById('reviewInterface').style.display = 'none';
        document.querySelector('.test-selection').style.display = 'block';
        
        this.currentTest = [];
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        clearInterval(this.timer);
    }
    
    // Progress saving methods
    saveProgress() {
        if (!this.currentSubject || !this.currentTest.length) return;
        
        const progress = {
            subject: this.currentSubject,
            currentQuestionIndex: this.currentQuestionIndex,
            userAnswers: this.userAnswers,
            timeRemaining: this.timeRemaining,
            testQuestions: this.currentTest.map(q => ({
                question_number: q.question_number,
                question: q.question,
                options: q.options,
                correct_answer: q.correct_answer
            })),
            timestamp: Date.now()
        };
        
        localStorage.setItem(`jcl_test_progress_${this.currentSubject}`, JSON.stringify(progress));
        console.log('Progress saved for', this.currentSubject);
    }
    
    loadProgress(subject) {
        try {
            const saved = localStorage.getItem(`jcl_test_progress_${subject}`);
            if (!saved) return null;
            
            const progress = JSON.parse(saved);
            
            // Check if progress is older than 24 hours
            const hoursSinceSaved = (Date.now() - progress.timestamp) / (1000 * 60 * 60);
            if (hoursSinceSaved > 24) {
                localStorage.removeItem(`jcl_test_progress_${subject}`);
                return null;
            }
            
            return progress;
        } catch (error) {
            console.error('Error loading progress:', error);
            return null;
        }
    }
    
    resumeTest(progress) {
        // Hide test selection, show test interface
        document.querySelector('.test-selection').style.display = 'none';
        document.getElementById('testInterface').style.display = 'block';
        document.getElementById('results').style.display = 'none';
        
        // Restore test state
        this.currentSubject = progress.subject;
        this.currentTest = progress.testQuestions;
        this.currentQuestionIndex = progress.currentQuestionIndex;
        this.userAnswers = progress.userAnswers;
        this.timeRemaining = progress.timeRemaining;
        
        // Start timer
        this.startTimer();
        
        // Display current question
        this.displayQuestion();
        
        console.log('Test resumed from question', this.currentQuestionIndex + 1);
    }
    
    clearProgress() {
        if (this.currentSubject) {
            localStorage.removeItem(`jcl_test_progress_${this.currentSubject}`);
        }
    }
}

// Initialize the test generator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new TestGenerator();
});
