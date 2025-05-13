import { formatDateTime, formatParagraph } from "../../utils.js";

class CuriosityTemplate {
  constructor() {
    const template = document
      .getElementById("curiosity-template")
      .cloneNode(true);
    this.elements = {
      template,
      item: template.querySelector(".curiosity-item"),
      display: {
        timestamp: template.querySelector(".curiosity-timestamp"),
        noteText: template.querySelector(".curiosity-note-text"),
        textContent: template.querySelector(".curiosity-text"),
      },
    };
  }

  render(curiosity) {
    const { item, display } = this.elements;
    display.timestamp.textContent = formatDateTime(curiosity.timestamp);
    display.noteText.textContent = formatParagraph(curiosity.note_text || "");
    display.textContent.textContent = formatParagraph(
      curiosity.curiosity_text || "",
    );
    return item;
  }

  registerClickListener(callback) {
    this.elements.item.addEventListener("click", callback);
  }
}

export default CuriosityTemplate;
