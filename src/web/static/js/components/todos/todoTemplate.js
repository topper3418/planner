import { formatDateTime, getLocalTime } from "../../utils.js";

class TodoTemplate {
  constructor() {
    const template = document.getElementById("todo-template").cloneNode(true);
    this.elements = {
      template,
      wrapper: template.content.querySelector(".todo-template-wrapper"),
      item: template.content.querySelector(".todo-template-item"),
      display: {
        checkbox: template.content.querySelector(".todo-template-checkbox"),
        main: template.content.querySelector(".todo-template-main"),
        details: template.content.querySelector(".todo-template-details"),
        collapse: template.content.querySelector(".todo-template-collapse"),
      },
      childrenContainer: template.content.querySelector(
        ".todo-template-children",
      ),
    };
    this.todo = null;
    this.now = getLocalTime();
    this.collapsed = false;
  }

  isLate() {
    const endTime = this.todo.target_end_time
      ? new Date(this.todo.target_end_time)
      : null;
    return endTime && endTime < this.now;
  }

  isStarted() {
    const startTime = this.todo.target_start_time
      ? new Date(this.todo.target_start_time)
      : null;
    return startTime && startTime < this.now;
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
    this.elements.display.checkbox.checked = todo.complete;
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
    this.elements.item.classList.add(colorClass);
    this.elements.display.main.textContent = mainText;
    this.elements.display.details.textContent = detailsText;
    if (todo.children && todo.children.length > 0) {
      this.elements.childrenContainer.innerHTML = ""; // Clear previous children
      this.elements.display.collapse.addEventListener("click", () => {
        this.toggleCollapse();
      });
      todo.children.forEach((child) => {
        const childTemplate = new TodoTemplate();
        const childElement = childTemplate.render(child);
        this.elements.childrenContainer.appendChild(childElement);
      });
      return this.elements.wrapper;
    } else {
      // no children, no need for a collapse.
      // instead of hiding it and affecting the layout, I'll make it invisible.
      this.elements.display.collapse.classList.add("text-transparent");
      return this.elements.item;
    }
  }

  toggleCollapse() {
    if (this.collapsed) {
      this.expandChildren();
    } else {
      this.collapseChildren();
    }
    this.collapsed = !this.collapsed;
  }

  collapseChildren() {
    this.elements.childrenContainer.classList.toggle("hidden");
    this.elements.display.collapse.classList.toggle("-rotate-90");
  }

  expandChildren() {
    this.elements.childrenContainer.classList.remove("hidden");
    this.elements.display.collapse.classList.remove("-rotate-90");
  }

  // TODO: deprecate this, I don't think I like the drilldown thing on anything but notes.
  registerClickListener(callback) {
    //this.elements.item.addEventListener("click", () => {
    //  callback(this.todo.id);
    //});
  }
}

export default TodoTemplate;
