// ==================== State Management ====================
let currentGene = null;
let currentAnswers = {};
let currentQuestions = [];
let currentResults = null;
const API_BASE = 'http://localhost:5000/api';

// ==================== Navigation Functions ====================
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
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

    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'loading-message';
    loadingMsg.innerHTML = '<div class="spinner"></div> Loading gene data...';
    document.body.appendChild(loadingMsg);

    try {
        const [geneResponse, questionsResponse] = await Promise.all([
            fetch(`${API_BASE}/gene/${geneName}`),
            fetch(`${API_BASE}/questions/${geneName}`)
        ]);

        const geneData = await geneResponse.json();
        const questionsData = await questionsResponse.json();

        if (!geneData.success || !questionsData.success) {
            throw new Error('Failed to load gene data');
        }

        currentQuestions = questionsData.data;
        loadingMsg.remove();

        displayQuestionnaire(geneData.data, currentQuestions);
        showScreen('screen-questionnaire');
        celebrateAction();
    } catch (error) {
        loadingMsg.remove();
        console.error('Error loading gene data:', error);
        alert('⚠️ Error loading gene data. Please check the backend is running and try again.');
    }
}

// ==================== Questionnaire Display ====================
function displayQuestionnaire(geneData, questions) {
    const geneInfo = geneData.gene;
    document.getElementById('gene-title').textContent = `${geneInfo.gene_name} — ${geneInfo.disease}`;
    document.getElementById('gene-description').textContent = geneInfo.description;

    const container = document.getElementById('questions-container');
    container.innerHTML = '';
    updateProgress();

    questions.forEach((q, index) => {
        const group = document.createElement('div');
        group.className = 'question-group';

        const label = document.createElement('label');
        label.textContent = `${index + 1}. ${q.question}`;
        group.appendChild(label);

        const optionsEl = document.createElement('div');
        optionsEl.className = 'answer-options';

        ['Yes', 'Maybe', 'No'].forEach(option => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = option;
            btn.onclick = () => selectAnswer(index, option, btn, optionsEl);
            optionsEl.appendChild(btn);
        });

        group.appendChild(optionsEl);
        container.appendChild(group);
    });
}

function selectAnswer(index, value, btn, optionsEl) {
    optionsEl.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    currentAnswers[index] = value;
    updateProgress();

    if (Object.keys(currentAnswers).length === currentQuestions.length) {
        setTimeout(submitDiagnosis, 600);
    }
}

function updateProgress() {
    const total = currentQuestions.length;
    const answered = Object.keys(currentAnswers).length;
    const pct = total > 0 ? (answered / total) * 100 : 0;
    document.getElementById('progress-fill').style.width = `${pct}%`;
    document.getElementById('question-counter').textContent = `${answered} of ${total} answered`;
}

// ==================== Diagnosis ====================
async function submitDiagnosis() {
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'loading-message';
    loadingMsg.innerHTML = '<div class="spinner"></div> Analyzing your responses...';
    document.body.appendChild(loadingMsg);

    try {
        const answersMap = {};
        currentQuestions.forEach((q, i) => {
            answersMap[q.id || q.question] = currentAnswers[i];
        });

        const response = await fetch(`${API_BASE}/diagnose/${currentGene}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: answersMap })
        });

        const data = await response.json();
        loadingMsg.remove();

        if (!data.success) throw new Error(data.message || 'Diagnosis failed');

        currentResults = data;
        displayResults(data.diagnosis);
        showScreen('screen-results');
    } catch (error) {
        loadingMsg.remove();
        console.error('Diagnosis error:', error);
        alert('⚠️ Error performing diagnosis. Please try again.');
    }
}

// ==================== Results Display ====================
function displayResults(diagnosis) {
    const container = document.getElementById('diagnosis-container');
    const score = Math.round((diagnosis.confidence_score || 0) * 100);
    const isPositive = diagnosis.status === 'positive' || score >= 50;

    container.innerHTML = `
        <div class="diagnosis-header">
            <div class="gene-name">${diagnosis.gene}</div>
            <div class="confidence-score">${score}%</div>
        </div>
        <div class="status-badge ${isPositive ? 'status-positive' : 'status-negative'}">
            ${isPositive ? '⚠️ Risk Detected' : '✅ Low Risk'}
        </div>
        <div class="detail-item">
            <div class="detail-label">Risk Level</div>
            <div class="detail-value">${diagnosis.risk_level || 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Status</div>
            <div class="detail-value">${diagnosis.status || 'N/A'}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Confidence Score</div>
            <div class="detail-value">${score}% match with genetic risk profile</div>
        </div>
    `;

    const recContainer = document.getElementById('recommendations');
    recContainer.innerHTML = '';

    const diet = diagnosis.gene_info?.diet;
    if (diet) {
        const cards = [
            { icon: '🥗', title: 'Dietary Recommendations', content: diet.recommendations },
            { icon: '💊', title: 'Supplements', content: diet.supplements },
            { icon: '🚫', title: 'Foods to Avoid', content: diet.restricted_foods },
            { icon: '✅', title: 'Recommended Foods', content: diet.allowed_foods }
        ];

        cards.forEach(({ icon, title, content }) => {
            if (!content) return;
            const card = document.createElement('div');
            card.className = 'recommendation-card';
            card.innerHTML = `<h4>${icon} ${title}</h4><p>${content}</p>`;
            recContainer.appendChild(card);
        });
    } else {
        recContainer.innerHTML = '<p style="color: var(--light-text)">No specific dietary recommendations available for this gene.</p>';
    }
}

// ==================== Download Report ====================
function downloadReport() {
    if (!currentResults) return;

    const diagnosis = currentResults.diagnosis;
    const score = Math.round((diagnosis.confidence_score || 0) * 100);
    const diet = diagnosis.gene_info?.diet || {};

    const report = [
        'NUTRIGENE GENETIC DIAGNOSIS REPORT',
        '====================================',
        `Generated: ${new Date().toLocaleDateString()}`,
        '',
        `GENE ANALYZED:    ${diagnosis.gene}`,
        `CONFIDENCE SCORE: ${score}%`,
        `STATUS:           ${diagnosis.status || 'N/A'}`,
        `RISK LEVEL:       ${diagnosis.risk_level || 'N/A'}`,
        '',
        'DIETARY RECOMMENDATIONS',
        '-----------------------',
        diet.recommendations || 'N/A',
        '',
        'SUPPLEMENTS',
        '-----------',
        diet.supplements || 'N/A',
        '',
        'FOODS TO AVOID',
        '--------------',
        diet.restricted_foods || 'N/A',
        '',
        'RECOMMENDED FOODS',
        '-----------------',
        diet.allowed_foods || 'N/A',
        '',
        '====================================',
        'DISCLAIMER: This report is for informational purposes only.',
        'Not a substitute for professional medical advice.'
    ].join('\n');

    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `NutriGene_Report_${diagnosis.gene}_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// ==================== Celebration Animation ====================
function celebrateAction() {
    const el = document.createElement('div');
    el.style.cssText = `
        position: fixed; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3rem; z-index: 9999; pointer-events: none;
        animation: celebratePop 0.8s ease-out forwards;
    `;
    el.textContent = '🧬';
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 800);
}