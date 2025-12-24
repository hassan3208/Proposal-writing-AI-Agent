// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// DOM Elements
const proposalForm = document.getElementById('proposalForm');
const submitBtn = document.getElementById('submitBtn');
const formCard = document.getElementById('formCard');
const resultsCard = document.getElementById('resultsCard');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');
const downloadBtn = document.getElementById('downloadBtn');
const generateNewBtn = document.getElementById('generateNewBtn');

// Store proposal data for PDF download
let currentProposalData = null;
let FULL_PROPOSAL = "";
let CLIENT_NAME = "";
let BUSINESS_NAME = "";


// Form submission
proposalForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form values
    const clientName = document.getElementById('clientName').value.trim();
    const apiKey = document.getElementById('apiKey').value.trim();
    const userInput = document.getElementById('userInput').value.trim();

    // Validate
    if (!apiKey || !userInput) {
        showError('Please fill in all required fields');
        return;
    }

    if (userInput.length < 10) {
        showError('Project requirements must be at least 10 characters');
        return;
    }

    // Show loading state
    setLoading(true);
    hideError();

    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/generate-proposal`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                client_name: clientName,
                user_input: userInput,
                api_key: apiKey
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate proposal');
        }

        const data = await response.json();
        FULL_PROPOSAL = data.full_proposal;
        CLIENT_NAME = data.client_name;
        currentProposalData = data;

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while generating the proposal');
    } finally {
        setLoading(false);
    }
});

// Display results
function displayResults(data) {
    // Populate results
    document.getElementById('projectScope').textContent = data.project_scope || 'N/A';
    document.getElementById('estimatedTimeline').textContent =
        `${data.estimated_timeline || 'N/A'} weeks`;
    document.getElementById('pricing').textContent = data.pricing || 'N/A';
    document.getElementById('justification').textContent = data.justification || 'N/A';

    // Hide form, show results
    formCard.style.display = 'none';
    resultsCard.style.display = 'block';

    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Download PDF
// Download PDF (FINAL FIX)
downloadBtn.addEventListener('click', async () => {
    if (!FULL_PROPOSAL) {
        showError('No proposal data available');
        return;
    }

    const originalText = downloadBtn.innerHTML;
    downloadBtn.innerHTML = `
        <span class="spinner"></span>
        Downloading...
    `;
    downloadBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/download-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                full_proposal: FULL_PROPOSAL,
                client_name: CLIENT_NAME,
                business_name: BUSINESS_NAME
            })
        });

        if (!response.ok) {
            throw new Error('Failed to download PDF');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `proposal_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();

        a.remove();
        window.URL.revokeObjectURL(url);

        downloadBtn.innerHTML = originalText;
        downloadBtn.disabled = false;

    } catch (error) {
        console.error(error);
        showError('Failed to download PDF. Please try again.');
        downloadBtn.innerHTML = originalText;
        downloadBtn.disabled = false;
    }
});



// Generate new proposal
generateNewBtn.addEventListener('click', () => {
    // Reset form
    proposalForm.reset();
    currentProposalData = null;

    // Show form, hide results
    resultsCard.style.display = 'none';
    formCard.style.display = 'block';

    // Scroll to form
    formCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// Loading state
function setLoading(isLoading) {
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');

    if (isLoading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
        submitBtn.disabled = true;
    } else {
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
        submitBtn.disabled = false;
    }
}

// Error handling
function showError(message) {
    errorMessage.textContent = message;
    errorAlert.style.display = 'flex';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    errorAlert.style.display = 'none';
}

function closeError() {
    hideError();
}

// Make closeError available globally
window.closeError = closeError;

// Add smooth reveal animation for form inputs
document.querySelectorAll('.input-field').forEach((input, index) => {
    input.style.opacity = '0';
    input.style.transform = 'translateY(20px)';

    setTimeout(() => {
        input.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        input.style.opacity = '1';
        input.style.transform = 'translateY(0)';
    }, 100 * index);
});
