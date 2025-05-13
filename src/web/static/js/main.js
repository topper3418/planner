import {
  FilterModal,
  QueryModal,
  NotesContent,
  TodosContent,
  CuriositiesContent,
} from "./components";
import ActionsContent from "./components/actions";
import DetailModal from "./components/detailModal";
import { createNote } from "./client";

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
    this.tabEnum = {
      notes: this.components.containers.notes,
      todos: this.components.containers.todos,
      actions: this.components.containers.actions,
      curiosities: this.components.containers.curiosities,
    };
    this.currentTab = "notes";
    this.configure();
    this.refresh = this.refresh.bind(this);
  }

  refresh() {
    this.tabEnum[tab].fetchAndRender();
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
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new Planner();
});
