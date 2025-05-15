import {
  FilterModal,
  QueryModal,
  NotesContent,
  TodosContent,
  CuriositiesContent,
  ActionsContent,
  DataModal,
  TabButton,
} from "./components/index.js";
import { createNote } from "./client/notes.js";

class Planner {
  constructor() {
    this.components = {
      modals: {
        queryModal: new QueryModal(),
        filterModal: new FilterModal(),
        detailModal: new DataModal(),
      },
      containers: {
        notes: new NotesContent(),
        todos: new TodosContent(),
        actions: new ActionsContent(),
        curiosities: new CuriositiesContent(),
      },
      noteInput: document.getElementById("note-input"),
      buttons: {
        notes: new TabButton("notes"),
        todos: new TabButton("todos"),
        actions: new TabButton("actions"),
        curiosities: new TabButton("curiosities"),
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
    this.refresh = this.refresh.bind(this);
    this.switchTab = this.switchTab.bind(this);
    this.configure();
    this.switchTab("notes");
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
    console.log(
      "switching from ",
      this.tabDir[this.currentTab],
      "to",
      this.tabDir[tab],
    );
    if (this.currentTab !== tab) {
      this.tabDir[this.currentTab].button.setInactive();
      this.tabDir[this.currentTab].container.hide();
    }
    this.currentTab = tab;
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
    this.components.noteInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        this.components.buttons.addNote.click();
      }
    });
    // tab switching
    this.components.buttons.notes.registerClickCallback(this.switchTab);
    this.components.buttons.todos.registerClickCallback(this.switchTab);
    this.components.buttons.actions.registerClickCallback(this.switchTab);
    this.components.buttons.curiosities.registerClickCallback(this.switchTab);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new Planner();
});
