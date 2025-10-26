class TestGenerator {
    constructor() {
        this.allQuestions = {};
        this.currentTest = [];
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.timeRemaining = 50 * 60; // 50 minutes in seconds
        this.timer = null;
        this.currentSubject = null;
        
        this.initializeEventListeners();
        this.loadAllQuestions();
        this.setupHistoryNavigation();
        this.checkForSavedTest();
    }
    
    setupHistoryNavigation() {
        // Handle browser back button
        window.addEventListener('popstate', (event) => {
            if (event.state && event.state.page === 'test') {
                // Do nothing - we're already in test view
            } else {
                // Go back to test selection
                this.returnToSelection();
            }
        });
    }
    
    checkForSavedTest() {
        const savedTest = localStorage.getItem('jcl_test_progress');
        if (savedTest) {
            this.showContinueDialog();
        }
    }
    
    showContinueDialog() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Continue Saved Test?</h3>
                <p>You have an unfinished test. Would you like to continue?</p>
                <div class="modal-buttons">
                    <button class="modal-btn modal-btn-yes" id="continueYes">Yes</button>
                    <button class="modal-btn modal-btn-no" id="continueNo">No</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        document.getElementById('continueYes').addEventListener('click', () => {
            this.loadSavedTest();
            document.body.removeChild(modal);
        });
        
        document.getElementById('continueNo').addEventListener('click', () => {
            localStorage.removeItem('jcl_test_progress');
            document.body.removeChild(modal);
        });
    }
    
    saveTestProgress() {
        const testData = {
            subject: this.currentSubject,
            currentTest: this.currentTest,
            currentQuestionIndex: this.currentQuestionIndex,
            userAnswers: this.userAnswers,
            timeRemaining: this.timeRemaining
        };
        localStorage.setItem('jcl_test_progress', JSON.stringify(testData));
    }
    
    loadSavedTest() {
        const savedData = JSON.parse(localStorage.getItem('jcl_test_progress'));
        if (savedData) {
            this.currentSubject = savedData.subject;
            this.currentTest = savedData.currentTest;
            this.currentQuestionIndex = savedData.currentQuestionIndex;
            this.userAnswers = savedData.userAnswers;
            this.timeRemaining = savedData.timeRemaining;
            
            // Show test interface
            document.querySelector('.test-selection').style.display = 'none';
            document.getElementById('testInterface').style.display = 'block';
            
            // Push state for back button
            history.pushState({ page: 'test' }, '', '#test');
            
            // Start timer and display
            this.startTimer();
            this.displayQuestion();
        }
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
        
        // Hide test selection, show test interface
        document.querySelector('.test-selection').style.display = 'none';
        document.getElementById('testInterface').style.display = 'block';
        document.getElementById('results').style.display = 'none';
        
        // Push state for back button functionality
        history.pushState({ page: 'test' }, '', '#test');
        
        // Generate random 50 questions from all years for this subject
        this.generateRandomTest(subject);
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.timeRemaining = 50 * 60;
        
        // Start timer
        this.startTimer();
        
        // Display first question
        this.displayQuestion();
        
        // Save initial progress
        this.saveTestProgress();
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
        
        // Display instruction if available
        const instructionBox = document.getElementById('instructionBox');
        const instructionText = document.getElementById('instructionText');
        if (question.question_instruction) {
            instructionText.textContent = question.question_instruction;
            instructionBox.style.display = 'block';
        } else {
            instructionBox.style.display = 'none';
        }
        
        // Display question - filter out "Question X" pattern
        let questionText = question.question_body || question.question || '';
        // Remove "Question X" or "Question X." at the start
        questionText = questionText.replace(/^Question\s+\d+\.?\s*/i, '');
        document.getElementById('questionText').textContent = questionText;
        
        // Display options
        const optionsContainer = document.getElementById('optionsContainer');
        optionsContainer.innerHTML = '';
        
        Object.entries(question.question_options || question.options).forEach(([key, value]) => {
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
        
        // Update visual selection
        document.querySelectorAll('.option').forEach(option => {
            option.classList.remove('selected');
        });
        document.querySelector(`input[value="${answer}"]`).parentElement.classList.add('selected');
        
        // Save progress
        this.saveTestProgress();
    }
    
    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayQuestion();
            this.saveTestProgress();
        }
    }
    
    nextQuestion() {
        if (this.currentQuestionIndex < 49) {
            this.currentQuestionIndex++;
            this.displayQuestion();
            this.saveTestProgress();
        }
    }
    
    startTimer() {
        this.timer = setInterval(() => {
            this.timeRemaining--;
            const minutes = Math.floor(this.timeRemaining / 60);
            const seconds = this.timeRemaining % 60;
            document.getElementById('timeRemaining').textContent = 
                `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (this.timeRemaining <= 0) {
                this.submitTest();
            }
        }, 1000);
    }
    
    submitTest() {
        clearInterval(this.timer);
        
        // Clear saved progress since test is complete
        localStorage.removeItem('jcl_test_progress');
        
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
            
            // Filter out "Question X" pattern for review too
            let questionText = question.question_body || question.question || '';
            questionText = questionText.replace(/^Question\s+\d+\.?\s*/i, '');
            
            const instructionHTML = question.question_instruction ? 
                `<div class="review-instruction">${question.question_instruction}</div>` : '';
            
            questionDiv.innerHTML = `
                <div class="question-header">
                    <h4>Question ${index + 1} ${isCorrect ? '✓' : '✗'}</h4>
                    <span class="status ${isCorrect ? 'correct' : 'incorrect'}">
                        ${isCorrect ? 'Correct' : 'Incorrect'}
                    </span>
                </div>
                ${instructionHTML}
                <div class="question-text">${questionText}</div>
                <div class="options-review">
                    ${Object.entries(question.question_options || question.options).map(([key, value]) => `
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
    
    returnToSelection() {
        // Reset everything and go back to test selection
        document.getElementById('testInterface').style.display = 'none';
        document.getElementById('results').style.display = 'none';
        document.getElementById('reviewInterface').style.display = 'none';
        document.querySelector('.test-selection').style.display = 'block';
        
        clearInterval(this.timer);
        
        // Update URL
        if (window.location.hash) {
            history.pushState(null, '', window.location.pathname);
        }
    }
    
    newTest() {
        // Clear saved progress
        localStorage.removeItem('jcl_test_progress');
        
        this.currentTest = [];
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.currentSubject = null;
        
        this.returnToSelection();
    }
}

// Initialize the test generator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new TestGenerator();
});
