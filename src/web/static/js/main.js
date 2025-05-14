import {
  FilterModal,
  QueryModal,
  NotesContent,
  TodosContent,
  CuriositiesContent,
  ActionsContent,
  DetailModal,
} from "./components/index.js";
import { createNote } from "./client/notes.js";

class Planner {
  constructor() {
    this.components = {
      modals: {
        queryModal: new QueryModal(),
        filterModal: new FilterModal(),
        detailModal: new DetailModal(),
      },
      containers: {
        notes: new NotesContent(),
        todos: new TodosContent(),
        actions: new ActionsContent(),
        curiosities: new CuriositiesContent(),
      },
      noteInput: document.getElementById("note-input"),
      buttons: {
        notes: document.getElementById("notes-button"),
        todos: document.getElementById("todos-button"),
        actions: document.getElementById("actions-button"),
        curiosities: document.getElementById("curiosities-button"),
        addNote: document.getElementById("add-note-button"),
      },
    };
    this.tabDir = {
      notes: {
        container: this.components.containers.notes,
        button: this.components.buttons.notes,
      },
      todos: {
        container: this.components.containers.todos,
        button: this.components.buttons.todos,
      },
      actions: {
        container: this.components.containers.actions,
        button: this.components.buttons.actions,
      },
      curiosities: {
        container: this.components.containers.curiosities,
        button: this.components.buttons.curiosities,
      },
    };
    this.currentTab = "notes";
    this.configure();
    this.switchTab("notes");
    this.refresh = this.refresh.bind(this);
  }

  refresh() {
    this.tabDir[this.currentTab].container.fetchAndRender();
  }

  switchTab(tab) {
    // make sure its a valid tab
    if (!this.tabDir[tab]) {
      console.error(`Invalid tab: ${tab}`);
      return;
    }
    // hide current tab if not the same as the new tab
    // and switch the button styles
    if (this.currentTab !== tab) {
      console.log(`Switching from ${this.currentTab} to ${tab}`);
      this.tabDir[this.currentTab].container.hide();
      this.tabDir[this.currentTab].button.classList.remove(
        "bg-white",
        "text-blue-500",
      );
      this.tabDir[this.currentTab].button.classList.add(
        "bg-blue-500",
        "text-white",
      );
      this.tabDir[tab].button.classList.remove("bg-blue-500", "text-white");
      this.tabDir[tab].button.classList.add("bg-white", "text-blue-500");
      this.currentTab = tab;
    }
    this.tabDir[tab].container.show();
    this.refresh();
  }

  configure() {
    // notes content
    this.components.containers.notes.registerRenderDetailModalCallback(
      this.components.modals.detailModal.setContent,
    );
    this.components.containers.notes.registerGetFiltersCallback(
      this.components.modals.filterModal.getValues,
    );
    // todos content
    this.components.containers.todos.registerRenderDetailModalCallback(
      this.components.modals.detailModal.setContent,
    );
    this.components.containers.todos.registerGetFiltersCallback(
      this.components.modals.filterModal.getValues,
    );
    // actions content
    this.components.containers.actions.registerRenderDetailModalCallback(
      this.components.modals.detailModal.setContent,
    );
    this.components.containers.actions.registerGetFiltersCallback(
      this.components.modals.filterModal.getValues,
    );
    // curiosities content
    this.components.containers.curiosities.registerRenderDetailModalCallback(
      this.components.modals.detailModal.setContent,
    );
    this.components.containers.curiosities.registerGetFiltersCallback(
      this.components.modals.filterModal.getValues,
    );
    // tabs
    this.components.buttons.notes.addEventListener("click", () => {
      this.switchTab("notes");
    });
    this.components.buttons.todos.addEventListener("click", () => {
      this.switchTab("todos");
    });
    this.components.buttons.actions.addEventListener("click", () => {
      this.switchTab("actions");
    });
    this.components.buttons.curiosities.addEventListener("click", () => {
      this.switchTab("curiosities");
    });
    // filter modal
    this.components.modals.filterModal.registerApplyCallback(this.refresh());
    // note input
    this.components.buttons.addNote.addEventListener("click", async () => {
      const noteText = this.components.noteInput.value.trim();
      if (!noteText) {
        alert("Please enter a note");
        return;
      }
      try {
        await createNote(noteText);
        this.components.noteInput.value = "";
        this.refresh();
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new Planner();
});
