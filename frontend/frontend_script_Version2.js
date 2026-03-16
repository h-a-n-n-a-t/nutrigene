// ==================== State Management ====================
let currentGene = null;
let currentAnswers = {};
let currentQuestions = [];
const API_BASE = 'http://localhost:5000/api';

// ==================== Navigation Functions ====================
function showScreen(screenId) {
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
    
    // Scroll to top with animation
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function goToWelcome() {
    showScreen('screen-welcome');
}

function goToGeneSelection() {
    showScreen('screen-gene-selection');
    currentAnswers = {};
}

function showAbout() {
    showScreen('screen-about');
}

// ==================== Gene Selection ====================
async function selectGene(geneName) {
    currentGene = geneName;
    currentAnswers = {};
    
    try {
        // Show loading animation
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'loading-message';
        loadingMsg.innerHTML = '<div class="spinner"></div> Loading gene data...';
        document.body.appendChild(loadingMsg);
        
        // Fetch gene information
        const geneResponse = await fetch(`${API_BASE}/gene/${geneName}`);
        const geneData = await geneResponse.json();
        
        // Fetch questions for this gene
        const questionsResponse = await fetch(`${API_BASE}/questions/${geneName}`);
        const questionsData = await questionsResponse.json();
        
        currentQuestions = questionsData.data;
        
        // Remove loading message
        loadingMsg.remove();
        
        // Display questionnaire
        displayQuestionnaire(geneData.data, currentQuestions);
        showScreen('screen-questionnaire');
        
        // Add celebration animation
        celebrateAction();
    } catch (error) {
        console.error('Error loading gene data:', error);
        alert('⚠️ Error loading gene data. Please try again.');
    }
}

// ==================== Questionnaire Display ====================
function displayQuestionnaire(geneData, questions) {
    const geneInfo = geneData.gene;
    const title = document.getElementById('gene-title');
    const description = document.getElementById('gene-description');
    const container = document.getElementById('questions-container');
    
    title.textContent = `${geneInfo.gene_name} - ${geneInfo.disease}`;
    description.textContent = geneInfo.description;
    
    // Clear previous questions
    container.innerHTML = '';
    
    // Display questions
    questions.forEach((q, index) => {
        const questionGroup = document.createElement('div');
        questionGroup.className = 'question-group';
        
        const label = document.createElement('label');
        label.textContent = q.question;
        questionGroup.appendChild(label);
        
        const answerOptions = document.createElement('div');
        answerOptions.className = 'answer-options';
        
        ['Yes', 'Maybe', 'No'].forEach((option, optionIndex) => {
            const btn = document.createElement