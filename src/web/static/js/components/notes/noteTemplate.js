import { formatDateTime, formatParagraph } from "../../utils.js";

class NoteTemplate {
  constructor() {
    const template = document.getElementById("note-template").cloneNode(true);
    this.elements = {
      template,
      item: template.content.querySelector(".note-item"),
      display: {
        id: template.content.querySelector(".note-id"),
        timestamp: template.content.querySelector(".note-timestamp"),
        noteUnprocessed: template.content.querySelector(".note-unprocessed"),
        noteProcessed: template.content.querySelector(".note-processed"),
        error: template.content.querySelector(".note-error"),
        textContent: template.content.querySelector(".note-text-content"),
      },
    };
  }

  render(note) {
    console.log(`Rendering note ${note.id}`);
    const { template, item, display } = this.elements;
    display.id.textContent = `[${String(note.id).padStart(4, "0")}]`;
    display.timestamp.textContent = formatDateTime(note.timestamp);
    if (note.processed) {
      display.noteUnprocessed.textContent = "";
      let statusText = "";
      if (note.num_actions) statusText += `Actions: ${note.num_actions}`;
      if (note.num_todos)
        statusText += `${statusText ? " | " : ""}Todos: ${note.num_todos}`;
      if (!note.num_todos && !note.num_actions) statusText = "Note";
      display.noteProcessed.textContent = statusText;
    } else {
      display.noteProcessed.textContent = "";
      display.noteUnprocessed.textContent = "Unprocessed";
    }
    if (note.processing_error) {
      const errorDiv = display.error;
      errorDiv.textContent = `Error: ${note.processing_error}`;
      errorDiv.style.display = "block";
    }
    display.textContent.textContent = formatParagraph(
      note.processed_note_text || note.note_text,
    );
    return item;
  }

  registerClickListener(callback) {
    this.elements.item.addEventListener("click", callback);
  }
}

export default NoteTemplate;
