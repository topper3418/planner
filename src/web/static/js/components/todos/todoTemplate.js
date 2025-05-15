import { formatDateTime } from "../../utils.js";

class TodoTemplate {
  constructor() {
    const template = document.getElementById("todo-template").cloneNode(true);
    this.elements = {
      template,
      item: template.content.querySelector(".todo-item"),
      display: {
        checkbox: template.content.querySelector(".todo-checkbox"),
        main: template.content.querySelector(".todo-main"),
        details: template.content.querySelector(".todo-details"),
      },
      childrenContainer: template.content.querySelector(".todo-children"),
    };
    this.todo = null;
  }

  isLate() {
    const endTime = this.todo.target_end_time
      ? new Date(this.todo.target_end_time)
      : null;
    const now = new Date();
    return endTime && endTime < now;
  }

  isStarted() {
    const startTime = this.todo.target_start_time
      ? new Date(this.todo.target_start_time)
      : null;
    const now = new Date();
    return startTime && startTime < now;
  }

  isComplete() {
    return this.todo.complete;
  }

  isCancelled() {
    return this.todo.cancelled;
  }

  isScheduled() {
    const startTime = this.todo.target_start_time;
    const endTime = this.todo.target_end_time;
    return startTime || endTime;
  }

  getStatus() {
    if (this.isComplete()) return "complete";
    if (this.isCancelled()) return "cancelled";
    if (this.isLate()) return "late";
    if (this.isStarted()) return "started";
    if (this.isScheduled()) return "scheduled";
    return "new";
  }

  getTimeText() {
    const startTime = this.todo.target_start_time
      ? new Date(this.todo.target_start_time)
      : null;
    const endTime = this.todo.target_end_time
      ? new Date(this.todo.target_end_time)
      : null;
    if (startTime && endTime) {
      return `${formatDateTime(startTime)} -> ${formatDateTime(endTime)}`;
    } else if (startTime) {
      return `${formatDateTime(startTime)} -> *`;
    } else if (endTime) {
      return `* -> ${formatDateTime(endTime)}`;
    }
    return "* -> *";
  }

  render(todo) {
    this.todo = todo;
    const { item, display, childrenContainer } = this.elements;
    display.checkbox.checked = todo.complete;
    const mainText = `[${String(todo.id).padStart(4, "0")}]: ${todo.todo_text}`;
    const detailsText = this.getTimeText();
    const colorMap = {
      new: "text-gray-800",
      complete: "text-green-500",
      cancelled: "text-gray-400",
      late: "text-red-500",
      started: "text-yellow-500",
      scheduled: "text-gray-800",
    };
    const colorClass = colorMap[this.getStatus()] || "text-pink-500";
    item.classList.add(colorClass);
    item.querySelector(".todo-main").textContent = mainText;
    item.querySelector(".todo-details").textContent = detailsText;
    console.log("rendered todo, moving to its children", todo.children);
    if (todo.children && todo.children.length > 0) {
      childrenContainer.innerHTML = ""; // Clear previous children
      todo.children.forEach((child) => {
        const childTemplate = new TodoTemplate();
        const childElement = childTemplate.render(child);
        console.log("rendering child", childElement);
        childrenContainer.appendChild(childElement);
      });
    }
    return item;
  }

  registerClickListener(callback) {
    this.elements.item.addEventListener("click", () => {
      callback(this.todo.id);
    });
  }
}

export default TodoTemplate;
