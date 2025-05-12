import { formatDateTime } from "../utils";

class TodoTemplate {
  constructor() {
    const template = document.getElementById("todo-template").cloneNode(true);
    this.elements = {
      template,
      item: template.querySelector(".todo-item"),
      display: {
        checkbox: template.querySelector(".todo-checkbox"),
        main: template.querySelector(".todo-main"),
        details: template.querySelector(".todo-details"),
      },
    };
  }

  render(todo) {
    this.elements.display.checkbox.checked = todo.complete;
    let mainText = `[${String(todo.id).padStart(4, "0")}]: ${todo.todo_text}`;
    let detailsText = "";
    if (todo.target_start_time || todo.target_end_time) {
      detailsText += `${formatDateTime(todo.target_start_time) || "*"} -> ${formatDateTime(todo.target_end_time) || "*"}`;
    }
    const created = todo.source_annotation?.note?.timestamp || "";
    if (created)
      detailsText += `${detailsText ? " | " : ""}Created: ${formatDateTime(created)}`;
    if (todo.complete && todo.source_annotation?.note?.timestamp) {
      detailsText += `${detailsText ? " | " : ""}Done: ${formatDateTime(todo.source_annotation.note.timestamp)}`;
    }
    const now = new Date();
    const startTime = todo.target_start_time
      ? new Date(todo.target_start_time)
      : null;
    const endTime = todo.target_end_time
      ? new Date(todo.target_end_time)
      : null;
    const started = startTime && startTime < now;
    const late = endTime && endTime < now;
    const yellow = started && !late;
    const red = late;
    const green = todo.complete;
    const grey = todo.cancelled;
    const white = !started && !endTime;
    let colorClass = "text-gray-800";
    if (green) colorClass = "text-green-500";
    else if (grey) colorClass = "text-gray-400";
    else if (red) colorClass = "text-red-500";
    else if (yellow) colorClass = "text-yellow-500";
    else if (white) colorClass = "text-gray-800";
    else colorClass = "text-pink-500";
    this.elements.item.classList.add(colorClass);
    this.elements.item.querySelector(".todo-main").textContent = mainText;
    this.elements.item.querySelector(".todo-details").textContent = detailsText;
  }
}

export default TodoTemplate;
