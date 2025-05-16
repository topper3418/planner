import { formatDateTime, formatParagraph } from "../../utils.js";

class CuriosityTemplate {
  constructor() {
    const template = document
      .getElementById("curiosity-template")
      .cloneNode(true);
    this.elements = {
      template,
      item: template.content.querySelector(".curiosity-item"),
      display: {
        timestamp: template.content.querySelector(".curiosity-timestamp"),
        noteText: template.content.querySelector(".curiosity-note-text"),
        textContent: template.content.querySelector(".curiosity-text"),
      },
    };
    this.curiosity = null;
  }

  render(curiosity) {
    this.curiosity = curiosity;
    const { item, display } = this.elements;
    display.timestamp.textContent = formatDateTime(curiosity.note.timestamp);
    display.noteText.textContent = formatParagraph(
      curiosity.note.note_text || "",
    );
    display.textContent.textContent = formatParagraph(
      curiosity.curiosity_text || "",
    );
    return item;
  }

  registerClickListener(callback) {
    this.elements.item.addEventListener("click", () => {
      callback(this.curiosity.id);
    });
  }
}

export default CuriosityTemplate;
