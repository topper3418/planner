import { initQueryModal } from "./modules/queryModal.js";
import { initTabManager } from "./modules/tabManager.js";
import { showTab } from "./modules/tabManager.js";
import { initApi } from "./modules/api.js";
import { initDataModal } from "./modules/detailModal.js";
import { FilterModal, QueryModal } from "./components";

class App {
  constructor() {
    this.components = {
      modals: {
        queryModal: new QueryModal(),
        filterModal: new FilterModal(),
      },
      containers: {
        notes: new NotesContent(),
        todos: new TodosContent(),
        actions: new ActionsContent(),
        curiosities: new CuriositiesContent(),
      },
      buttons: {
        notes: document.getElementById("notes-button"),
        todos: document.getElementById("todos-button"),
        actions: document.getElementById("actions-button"),
        curiosities: document.getElementById("curiosities-button"),
      },
    };
    this.tabEnum = {
      notes: this.components.containers.notes,
      todos: this.components.containers.todos,
      actions: this.components.containers.actions,
      curiosities: this.components.containers.curiosities,
    };
    this.currentTab = "notes";
    this.server = new ServerApi();
  }

  switchTab(tab) {
    // make sure its a valid tab
    if (!this.tabEnum[tab]) {
      console.error(`Invalid tab: ${tab}`);
      return;
    }
    // hide current tab if not the same as the new tab
    if (this.currentTab !== tab) {
      this.tabEnum[this.currentTab].hide();
      this.currentTab = tab;
      this.tabEnum[tab].show();
    }
    this.tabEnum[tab].fetchAndRender();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const app = new App();
});
