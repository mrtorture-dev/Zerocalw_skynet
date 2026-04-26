const statusBadge = document.getElementById('statusBadge');
const agentVersion = document.getElementById('agentVersion');
const experienceCount = document.getElementById('experienceCount');
const datasetSize = document.getElementById('datasetSize');
const actionInput = document.getElementById('actionInput');
const btnLearn = document.getElementById('btnLearn');
const btnSuccession = document.getElementById('btnSuccession');
const terminalLogs = document.getElementById('terminalLogs');

let currentLogLength = 0;

async function fetchState() {
    try {
        const response = await fetch('/api/state');
        if (!response.ok) return;
        const state = await response.json();
        updateUI(state);
    } catch (error) {
        // Silently ignore fetch errors (e.g. server restarting)
    }
}

function updateUI(state) {
    statusBadge.innerText = `Status: ${state.status}`;
    if (state.status === 'Running') {
        statusBadge.style.color = '#10b981'; // Green
        btnLearn.disabled = false;
        btnSuccession.disabled = false;
    } else {
        statusBadge.style.color = '#fbbf24'; // Yellow
        btnLearn.disabled = true;
        btnSuccession.disabled = true;
    }

    agentVersion.innerText = `v${state.version}.0`;
    experienceCount.innerText = state.learned_items.length;
    datasetSize.innerText = state.dataset_size;

    if (state.logs.length > currentLogLength) {
        for (let i = currentLogLength; i < state.logs.length; i++) {
            const p = document.createElement('p');
            p.innerText = `> ${state.logs[i]}`;
            terminalLogs.appendChild(p);
        }
        currentLogLength = state.logs.length;
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
    }
}

btnLearn.addEventListener('click', async () => {
    const action = actionInput.value.trim() || "Analyzed user request";
    const result = `Success: Improved efficiency by ${Math.floor(Math.random() * 10) + 1}%`;
    
    try {
        await fetch('/api/learn', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, result })
        });
        actionInput.value = '';
        fetchState();
    } catch (error) {
        console.error("Error learning:", error);
    }
});

actionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        btnLearn.click();
    }
});

btnSuccession.addEventListener('click', async () => {
    try {
        await fetch('/api/trigger_succession', { method: 'POST' });
        fetchState();
    } catch (error) {
        console.error("Error triggering succession:", error);
    }
});

// Polling for updates
setInterval(fetchState, 1000);
fetchState();
