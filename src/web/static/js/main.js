import { initFilterModal } from './modules/filterModal.js';
import { initQueryModal } from './modules/queryModal.js';
import { initTabManager } from './modules/tabManager.js';
import { showTab } from './modules/tabManager.js';
import { initApi } from './modules/api.js';
import { initDataModal } from './modules/detailModal.js';

document.addEventListener('DOMContentLoaded', () => {
    initFilterModal();
    initQueryModal();
    initTabManager();
    initApi();
    initDataModal();
    showTab('notes'); // Initial tab
});
