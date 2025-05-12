import { getNotes, getNoteById } from "..client/notes";
import { NoteTemplate } from "./noteTemplate";

class NotesContent {
  constructor() {
    this.elements = {
      container: document.getElementById("notes-content"),
      addButton: document.getElementById("add-note-button"),
      filterButton: document.getElementById("filter-notes-button"),
    };
    this.getFiltersCallback = null;
    this.renderDetailModalCallback = null;
  }

  hide() {
    this.elements.container.classList.add("hidden");
  }

  show() {
    this.elements.container.classList.remove("hidden");
  }

  getFilters() {
    if (this.getFiltersCallback) {
      this.filters = this.getFiltersCallback();
    } else {
      console.error("getFiltersCallback is not set");
    }
    return this.filters;
  }

  async fetchAndRender() {
    const filters = this.getFilters();
    const notes = await getNotes(filters);
    this.renderNotes(notes);
  }

  renderNotes(notes) {
    const container = this.elements.container;
    container.innerHTML = ""; // Clear previous content
    notes.forEach((note) => {
      const noteTemplate = new NoteTemplate();
      const noteElement = noteTemplate.render(note);
      noteTemplate.registerClickListener(async (noteId) => {
        const noteDetails = await getNoteById(noteId);
        this.renderDetailModalCallback(noteDetails);
      });
      container.appendChild(noteElement);
    });
  }

  ///////////////////////////////////////////////////////////////////////////
  //                           HOOK REGISTRATIONS                          //
  ///////////////////////////////////////////////////////////////////////////
  registerGetFiltersCallback(callback) {
    this.getFiltersCallback = callback;
  }

  registerRenderDetailModalCallback(callback) {
    this.renderDetailModalCallback = callback;
  }
}

export default NotesContent;
