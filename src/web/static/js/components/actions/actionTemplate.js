import { formatDateTime } from "../../utils.js";

class ActionTemplate {
  constructor() {
    const template = document.getElementById("action-template").cloneNode(true);
    this.elements = {
      template,
      item: template.content.querySelector(".action-item"),
      display: {
        id: template.content.querySelector(".action-id"),
        timestamp: template.content.querySelector(".action-timestamp"),
        textContent: template.content.querySelector(".action-text-content"),
        todoText: template.content.querySelector(".action-todo-text"),
      },
    };
    this.action = null;
  }

  render(action) {
    this.action = action;
    const { item, display } = this.elements;
    display.id.textContent = `[${String(action.id).padStart(4, "0")}]`;
    display.timestamp.textContent = formatDateTime(action.timestamp);
    let actionText = action.action_text;
    if (action.todo_id && action.todo) {
      display.todoText.textContent = `-> ${action.todo.todo_text}`;
    }
    item.classList.add(
      action.mark_complete ? "text-green-500" : "text-gray-800",
    );
    display.textContent.textContent = actionText;
    return item;
  }

  registerClickListener(callback) {
    this.elements.item.addEventListener("click", () => {
      callback(this.action.id);
    });
  }
}

export default ActionTemplate;
