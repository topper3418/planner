import { fetchTabContent } from './api.js';

let currentTab = 'notes';

export function getCurrentTab() {
    return currentTab;
}

function isMetaKeyPressed(event) {
    const isMac = navigator.userAgent.includes('Mac');
    return isMac ? event.ctrlKey : (event.ctrlKey || event.altKey);
}

export function initTabManager() {
    const queryModal = document.getElementById('query-modal');
    const queryInput = document.getElementById('query-input');
    const noteInput = document.getElementById('note-input');

    // Attach event listeners to tab buttons
    const tabButtons = [
        { id: 'notes-button', tab: 'notes' },
        { id: 'todos-button', tab: 'todos' },
        { id: 'actions-button', tab: 'actions' },
        { id: 'curiosities-button', tab: 'curiosities' }
    ];

    tabButtons.forEach(({ id, tab }) => {
        const button = document.getElementById(id);
        if (button) {
            button.addEventListener('click', () => showTab(tab));
        }
    });

    document.addEventListener('keydown', (event) => {
        if (isMetaKeyPressed(event)) {
            const key = event.key.toLowerCase();
            let targetButton;

            switch (key) {
                case 'n':
                    event.preventDefault();
                    targetButton = document.getElementById('notes-button');
                    showTab('notes');
                    break;
                case 't':
                    event.preventDefault();
                    targetButton = document.getElementById('todos-button');
                    showTab('todos');
                    break;
                case 'a':
                    event.preventDefault();
                    targetButton = document.getElementById('actions-button');
                    showTab('actions');
                    break;
                case 'c':
                    event.preventDefault();
                    targetButton = document.getElementById('curiosities-button');
                    showTab('curiosities');
                    break;
                case 'q':
                    event.preventDefault();
                    targetButton = document.getElementById('query-modal-button');
                    document.dispatchEvent(new Event('clickQueryModal'));
                    break;
                case 'enter':
                    event.preventDefault();
                    const modalOpen = !queryModal.classList.contains('hidden');
                    const targetInput = modalOpen ? queryInput : noteInput;
                    targetInput.focus();
                    break;
            }

            if (targetButton) {
                targetButton.focus();
            }
        }
    });
}

export function showTab(tab) {
    currentTab = tab;
    document.getElementById('middle-content').innerHTML = '';
    document.getElementById('middle-content').dataset.currentTab = tab;

    const buttons = ['notes-button', 'todos-button', 'actions-button', 'curiosities-button'];
    buttons.forEach((btnId) => {
        const btn = document.getElementById(btnId);
        if (btnId === `${tab}-button`) {
            btn.classList.remove('bg-white', 'text-blue-500');
            btn.classList.add('bg-blue-500', 'text-white');
            btn.setAttribute('aria-pressed', 'true');
        } else {
            btn.classList.add('bg-white', 'text-blue-500');
            btn.classList.remove('bg-blue-500', 'text-white');
            btn.setAttribute('aria-pressed', 'false');
        }
    });

    fetchTabContent();
}
