class FilterModal {
  constructor() {
    this.elements = {
      containers: {
        modal: document.getElementById("filter-modal"),
        middleContent: document.getElementById("middle-content"),
        actionsFilter: document.getElementById("actions-filter"),
        todosFilter: document.getElementById("todos-filter"),
      },
      inputs: {
        search: document.getElementById("filter-search"),
        startTime: document.getElementById("filter-start-time"),
        endTime: document.getElementById("filter-end-time"),
        appliedToTodo: document.getElementById("filter-applied-to-todo"),
        notAppliedToTodo: document.getElementById("filter-not-applied-to-todo"),
        completed: document.getElementById("filter-completed"),
        cancelled: document.getElementById("filter-cancelled"),
        active: document.getElementById("filter-active"),
      },
      buttons: {
        openButton: document.getElementById("filter-modal-button"),
        closeButton: document.getElementById("filter-modal-close-button"),
        applyButton: document.getElementById("filter-apply-button"),
        clearButton: document.getElementById("filter-clear-button"),
      },
    };
    this.initialValues = {
      search: "",
      startTime: "",
      endTime: "",
      actions: { appliedToTodo: true, notAppliedToTodo: true },
      todos: { completed: false, cancelled: false, active: true },
    };
    this.clear();
    this.initClickListeners();
    this.getValues = this.getValues.bind(this);
  }

  update() {
    console.log("updating filter modal", this.elements);
    // get the current tab
    const tabButtons = document.querySelectorAll(".tab-button");
    const clickedTabButton = Array.from(tabButtons).find(
      (button) => button.getAttribute("aria-pressed") === "true",
    );
    const currentTab = clickedTabButton.id.replace("-button", "");
    // set the filter modal to the current tab
    this.elements.containers.actionsFilter.classList.toggle(
      "hidden",
      currentTab !== "actions",
    );
    this.elements.containers.todosFilter.classList.toggle(
      "hidden",
      currentTab !== "todos",
    );
  }

  open() {
    this.update();
    this.elements.containers.modal.classList.remove("hidden");
    this.elements.inputs.search.focus();
  }

  close() {
    this.elements.containers.modal.classList.add("hidden");
  }

  clear() {
    this.elements.inputs.search.value = this.initialValues.search;
    this.elements.inputs.startTime.value = this.initialValues.startTime;
    this.elements.inputs.endTime.value = this.initialValues.endTime;
    this.elements.inputs.appliedToTodo.checked =
      this.initialValues.actions.appliedToTodo;
    this.elements.inputs.notAppliedToTodo.checked =
      this.initialValues.actions.notAppliedToTodo;
    this.elements.inputs.completed.checked = this.initialValues.todos.completed;
    this.elements.inputs.cancelled.checked = this.initialValues.todos.cancelled;
  }

  initClickListeners() {
    this.elements.buttons.openButton.addEventListener("click", () =>
      this.open(),
    );
    this.elements.buttons.closeButton.addEventListener("click", () =>
      this.close(),
    );
    this.elements.buttons.clearButton.addEventListener("click", () => {
      this.clear();
      this.close();
    });
    // return to search when in the search input
    this.elements.inputs.search.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        this.elements.buttons.applyButton.click();
      }
    });
  }

  getValues() {
    return {
      search: this.elements.inputs.search.value.trim(),
      startTime: this.elements.inputs.startTime.value,
      endTime: this.elements.inputs.endTime.value,
      actions: {
        appliedToTodo: this.elements.inputs.appliedToTodo.checked,
        notAppliedToTodo: this.elements.inputs.notAppliedToTodo.checked,
      },
      todos: {
        completed: this.elements.inputs.completed.checked,
        cancelled: this.elements.inputs.cancelled.checked,
        active: this.elements.inputs.active.checked,
      },
    };
  }

  registerApplyCallback(callback) {
    this.elements.buttons.applyButton.addEventListener("click", () => {
      this.close();
      callback();
    });
    this.elements.buttons.clearButton.addEventListener("click", () => {
      this.close();
      callback();
    });
  }
}

export default FilterModal;
