import { getTodos, getTodoById } from "../../client/todos.js";
import TodoTemplate from "./todoTemplate.js";

class TodosContent {
  constructor() {
    this.elements = {
      container: document.getElementById("todos-content"),
    };
    this.getFiltersCallback = null;
    this.renderDetailModalCallback = null;
    this.hide = this.hide.bind(this);
    this.show = this.show.bind(this);
    this.fetchAndRender = this.fetchAndRender.bind(this);
  }

  hide() {
    this.elements.container.classList.add("hidden");
  }

  show() {
    this.elements.container.classList.remove("hidden");
  }

  getFilters() {
    if (this.getFiltersCallback) {
      this.filters = this.getFiltersCallback();
    } else {
      console.error("getFiltersCallback is not set");
    }
    return this.filters;
  }

  async fetchAndRender() {
    const filters = this.getFilters();
    const todos = await getTodos(filters);
    this.renderTodos(todos);
  }

  renderTodos(todos) {
    const container = this.elements.container;
    container.innerHTML = ""; // Clear previous content
    todos.forEach((todo) => {
      const todoTemplate = new TodoTemplate();
      const todoElement = todoTemplate.render(todo);
      todoTemplate.registerClickListener(async (todoId) => {
        const todoDetails = await getTodoById(todoId);
        this.renderDetailModalCallback(todoDetails);
      });
      container.appendChild(todoElement);
    });
  }

  ///////////////////////////////////////////////////////////////////////////
  //                           HOOK REGISTRATIONS                          //
  ///////////////////////////////////////////////////////////////////////////
  registerGetFiltersCallback(callback) {
    this.getFiltersCallback = callback;
  }
  registerRenderDetailModalCallback(callback) {
    this.renderDetailModalCallback = callback;
  }
}

export default TodosContent;
