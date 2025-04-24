import { getFilterValues } from './filterModal.js';
import { getCurrentTab } from './tabManager.js';
import { renderNote, renderTodo, renderAction, renderCuriosity, formatDateTimeFromUTC } from './renderUtils.js';

export async function fetchTabContent() {
    const filterValues = getFilterValues();
    const currentTab = getCurrentTab();
    try {
        const endpoint = currentTab === 'curiosities' ? '/api/curiosities' : `/api/${currentTab}`;
        console.log('Fetching data from:', endpoint, 'with filters:', filterValues);
        const params = new URLSearchParams();
        params.append('limit', '50');
        if (filterValues.search) params.append('search', filterValues.search);
        if (filterValues.startTime) params.append('startTime', formatDateTimeFromUTC(filterValues.startTime, true));
        if (filterValues.endTime) params.append('endTime', formatDateTimeFromUTC(filterValues.endTime, true));
        if (currentTab === 'notes' && filterValues.notes.category) {
            params.append('category', filterValues.notes.category);
        }
        if (currentTab === 'actions' && filterValues.actions.appliedToTodo) {
            params.append('hasTodo', 'true');
        }
        if (currentTab === 'todos') {
            params.append('completed', Boolean(filterValues.todos.completed));
            params.append('cancelled', Boolean(filterValues.todos.cancelled));
            params.append('active', Boolean(filterValues.todos.active));
        }
        console.log('Fetching data with params:', params.toString());
        const response = await fetch(`${endpoint}?${params.toString()}`, {
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        const contentDiv = document.getElementById('middle-content');
        contentDiv.innerHTML = '';
        let items = [];
        if (currentTab === 'notes') {
            items = (data.notes || []).map(note => renderNote(note));
        } else if (currentTab === 'todos') {
            items = (data.todos || []).map(todo => renderTodo(todo));
        } else if (currentTab === 'actions') {
            items = (data.actions || []).map(action => renderAction(action));
        } else if (currentTab === 'curiosities') {
            items = (data.curiosities || []).reverse().map(curiosity => renderCuriosity(curiosity));
        }
        if (items.length === 0) {
            contentDiv.textContent = `No ${currentTab} found`;
        } else {
            items.forEach(item => contentDiv.appendChild(item));
        }
        const scrollContainer = document.getElementById('middle-panel');
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
    } catch (error) {
        document.getElementById('middle-content').textContent = `Error: ${error.message}`;
    }
}

export async function createNote() {
    console.log('createNote function called');
    const noteInput = document.getElementById('note-input');
    const noteText = noteInput.value.trim();
    if (!noteText) {
        alert('Please enter a note');
        return;
    }
    try {
        const response = await fetch('/api/notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: { note: noteText } })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        noteInput.value = '';
        if (getCurrentTab() === 'notes') fetchTabContent();
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

export async function submitQueryApi(query) {
    console.log('submitQueryApi called with query:', query);
    try {
        const response = await fetch(`/api/summary?prompt=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (data.error) {
            return { error: data.error };
        }
        return { summary: data.summary };
    } catch (error) {
        return { error: error.message };
    }
}

export async function fetchDetails(type, id) {
    // make sure the type is valid
    const validTypes = ['notes', 'todos', 'actions', 'curiosities'];
    if (!validTypes.includes(type)) {
        throw new Error('Invalid type');
    }
    console.log('Fetching details for type:', type, 'with id:', id);
    try {
        const response = await fetch(`/api/${type}/${id}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        console.log('Details fetched successfully:', data);
        return data?.data;
    } catch (error) {
        console.error('Error fetching details:', error);
        throw error;
    }
}

export function initApi() {
    const addNoteButton = document.getElementById('add-note-button');
    if (addNoteButton) {
        addNoteButton.addEventListener('click', () => {
            console.log('Add note button clicked');
            document.dispatchEvent(new Event('createNote'));
        });
    }
    const noteInput = document.getElementById('note-input');
    if (noteInput) {
        noteInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.metaKey && !event.ctrlKey) {
                console.log('Enter key pressed in note input');
                event.preventDefault();
                document.dispatchEvent(new Event('createNote'));
            }
        });
    }

    // Listen for createNote event
    document.addEventListener('createNote', () => {
        console.log('createNote event received');
        createNote();
    });
}
