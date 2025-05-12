import { submitQueryApi } from './api.js';

export function initQueryModal() {
    const queryModal = document.getElementById('query-modal');
    const queryModalButton = document.getElementById('query-modal-button');
    const queryInput = document.getElementById('query-input');
    const queryResponse = document.getElementById('query-response');
    const querySubmitButton = document.getElementById('query-submit-button');
    const modalCloseButton = document.getElementById('modal-close-button');

    function openQueryModal() {
        queryModal.classList.remove('hidden');
        queryInput.focus();
    }

    function closeQueryModal() {
        queryModal.classList.add('hidden');
        queryModalButton.focus();
    }

    async function submitQuery() {
        console.log('submitQuery function called');
        const query = queryInput.value.trim();
        if (!query) {
            queryResponse.innerHTML = '<p class="text-red-500">Please enter a query</p>';
            return;
        }
        queryResponse.innerHTML = '<p>Processing query...</p>';
        const result = await submitQueryApi(query);
        if (result.error) {
            queryResponse.innerHTML = `<p class="text-red-500">Error: ${result.error}</p>`;
        } else {
            const paragraphs = result.summary.map(paragraph => `<p>${paragraph}</p>`).join('');
            queryResponse.innerHTML = `<h3>Response:</h3>${paragraphs}`;
        }
    }

    if (queryModalButton) {
        queryModalButton.addEventListener('click', openQueryModal);
    }
    if (modalCloseButton) {
        modalCloseButton.addEventListener('click', closeQueryModal);
    }
    if (querySubmitButton) {
        querySubmitButton.addEventListener('click', () => {
            console.log('Query submit button clicked');
            document.dispatchEvent(new Event('submitQuery'));
        });
    }
    if (queryInput) {
        queryInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                console.log('Enter key pressed in query input');
                event.preventDefault();
                document.dispatchEvent(new Event('submitQuery'));
            }
        });
    }

    document.addEventListener('clickQueryModal', openQueryModal);
    document.addEventListener('submitQuery', submitQuery);

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !queryModal.classList.contains('hidden')) {
            closeQueryModal();
        }
    });

    if (queryModal) {
        queryModal.addEventListener('click', (event) => {
            if (event.target === queryModal) {
                closeQueryModal();
            }
        });
    }
}
