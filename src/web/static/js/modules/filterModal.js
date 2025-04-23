import { fetchTabContent } from './api.js';

let filterValues = {
    search: '',
    startTime: '',
    endTime: '',
    notes: { category: '' },
    actions: { appliedToTodo: false },
    todos: { completed: false, cancelled: false, active: true }
};

export function getFilterValues() {
    return filterValues;
}

export function initFilterModal() {
    const filterModal = document.getElementById('filter-modal');
    const filterModalButton = document.getElementById('filter-modal-button');
    const filterModalCloseButton = document.getElementById('filter-modal-close-button');
    const filterApplyButton = document.getElementById('filter-apply-button');
    const filterClearButton = document.getElementById('filter-clear-button');
    const filterSearch = document.getElementById('filter-search');
    const filterStartTime = document.getElementById('filter-start-time');
    const filterEndTime = document.getElementById('filter-end-time');
    const filterCategory = document.getElementById('filter-category');
    const filterAppliedToTodo = document.getElementById('filter-applied-to-todo');
    const filterCompleted = document.getElementById('filter-completed');
    const filterCancelled = document.getElementById('filter-cancelled');
    const filterActive = document.getElementById('filter-active');

    function updateFilterModal() {
        const currentTab = document.getElementById('middle-content').dataset.currentTab || 'notes';
        document.getElementById('notes-filter').classList.toggle('hidden', currentTab !== 'notes');
        document.getElementById('actions-filter').classList.toggle('hidden', currentTab !== 'actions');
        document.getElementById('todos-filter').classList.toggle('hidden', currentTab !== 'todos');
        filterSearch.value = filterValues.search;
        filterStartTime.value = filterValues.startTime || '';
        filterEndTime.value = filterValues.endTime || '';
        filterCategory.value = filterValues.notes.category;
        filterAppliedToTodo.checked = filterValues.actions.appliedToTodo;
        filterCompleted.checked = filterValues.todos.completed;
        filterCancelled.checked = filterValues.todos.cancelled;
        filterActive.checked = filterValues.todos.active;
        filterStartTime.classList.toggle('empty-datetime', !filterValues.startTime);
        filterEndTime.classList.toggle('empty-datetime', !filterValues.endTime);
    }

    function openFilterModal() {
        updateFilterModal();
        filterModal.classList.remove('hidden');
        filterSearch.focus();
    }

    function closeFilterModal() {
        filterModal.classList.add('hidden');
        filterModalButton.focus();
    }

    function applyFilters() {
        filterValues.search = filterSearch.value.trim();
        filterValues.startTime = filterStartTime.value;
        filterValues.endTime = filterEndTime.value;
        filterValues.notes.category = filterCategory.value.trim();
        filterValues.actions.appliedToTodo = filterAppliedToTodo.checked;
        filterValues.todos.completed = filterCompleted.checked;
        filterValues.todos.cancelled = filterCancelled.checked;
        filterValues.todos.active = filterActive.checked;
        fetchTabContent();
        closeFilterModal();
    }

    function applyFilterOnEnter(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            applyFilters();
        }
    }

    function clearFilters() {
        filterValues = {
            search: '',
            startTime: '',
            endTime: '',
            notes: { category: '' },
            actions: { appliedToTodo: false },
            todos: { completed: true, cancelled: false, active: true }
        };
        filterSearch.value = '';
        filterStartTime.value = '';
        filterEndTime.value = '';
        filterCategory.value = '';
        filterAppliedToTodo.checked = false;
        filterCompleted.checked = true;
        filterCancelled.checked = false;
        filterActive.checked = true;
        filterStartTime.classList.add('empty-datetime');
        filterEndTime.classList.add('empty-datetime');
        fetchTabContent();
        closeFilterModal();
    }

    filterModalButton.addEventListener('click', openFilterModal);
    filterModalCloseButton.addEventListener('click', closeFilterModal);
    filterApplyButton.addEventListener('click', applyFilters);
    filterClearButton.addEventListener('click', clearFilters);
    filterSearch.addEventListener('input', applyFilterOnEnter);
    filterStartTime.addEventListener('input', applyFilterOnEnter);
    filterEndTime.addEventListener('input', applyFilterOnEnter);
    filterCategory.addEventListener('input', applyFilterOnEnter);
    filterAppliedToTodo.addEventListener('input', applyFilterOnEnter);
    filterCompleted.addEventListener('input', applyFilterOnEnter);
    filterCancelled.addEventListener('input', applyFilterOnEnter);
    filterActive.addEventListener('input', applyFilterOnEnter);

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !filterModal.classList.contains('hidden')) {
            closeFilterModal();
        }
        if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'f') {
            event.preventDefault();
            openFilterModal();
        }
    });

    filterModal.addEventListener('click', (event) => {
        if (event.target === filterModal) {
            closeFilterModal();
        }
    });
}
