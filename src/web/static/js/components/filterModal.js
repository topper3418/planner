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
        category: document.getElementById("filter-category"),
        appliedToTodo: document.getElementById("filter-applied-to-todo"),
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
      actions: { appliedToTodo: false },
      todos: { completed: false, cancelled: false, active: true },
    };
    this.clear();
    this.initClickListeners();
    this.getValues = this.getValues.bind(this);
  }

  update() {
    const currentTab =
      document.getElementById("middle-content").dataset.currentTab || "notes";
    this.elements.actionsFilter.classList.toggle(
      "hidden",
      currentTab !== "actions",
    );
    this.elements.todosFilter.classList.toggle(
      "hidden",
      currentTab !== "todos",
    );
  }

  open() {
    this.update();
    this.containers.modal.classList.remove("hidden");
    this.filterSearch.focus();
  }

  close() {
    this.elements.containers.modal.classList.add("hidden");
  }

  clear() {
    this.elements.inputs.search.value = this.initialValues.search;
    this.elements.inputs.startTime.value = this.initialValues.startTime;
    this.elements.inputs.endTime.value = this.initialValues.endTime;
    this.elements.inputs.category.value = this.initialValues.notes.category;
    this.elements.inputs.appliedToTodo.checked =
      this.initialValues.actions.appliedToTodo;
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
  }

  getValues() {
    return {
      search: this.elements.inputs.search.value.trim(),
      startTime: this.elements.inputs.startTime.value,
      endTime: this.elements.inputs.endTime.value,
      notes: { category: this.elements.inputs.category.value.trim() },
      actions: { appliedToTodo: this.elements.inputs.appliedToTodo.checked },
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
  }
}

export default FilterModal;
