import { formatDateTime } from "../../utils.js";

class ActionTemplate {
  constructor() {
    this.elements = {
      template: document.getElementById("action-template").cloneNode(true),
      item: template.querySelector(".action-item"),
      display: {
        id: template.querySelector(".action-id"),
        timestamp: template.querySelector(".action-timestamp"),
        textContent: template.querySelector(".action-text-content"),
      },
    };
  }

  render(action) {
    const { template, item, display } = this.elements;
    display.id.textContent = `[${String(action.id).padStart(4, "0")}]`;
    display.timestamp.textContent = formatDateTime(action.timestamp);
    let actionText = action.action_text;
    if (action.todo_id && action.todo) {
      actionText += ` -> ${action.todo.todo_text}`;
    }
    template.classList.add(
      action.mark_complete ? "text-green-500" : "text-gray-800",
    );
    display.textContent.textContent = actionText;
    return item;
  }

  registerClickListener(callback) {
    this.elements.item.addEventListener("click", callback);
  }
}

export default ActionTemplate;
