import { getActions, getAction } from "../../client";
import ActionTemplate from "./actionTemplate";

class ActionsContent {
  constructor() {
    this.elements = {
      container: document.getElementById("actions-content"),
    };
    this.getFiltersCallback = null;
    this.renderDetailModalCallback = null;
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
    const actions = await getActions(filters);
    this.renderActions(actions);
  }

  renderActions(actions) {
    const container = this.elements.container;
    container.innerHTML = ""; // Clear previous content
    actions.forEach((action) => {
      const actionTemplate = new ActionTemplate();
      const actionElement = actionTemplate.render(action);
      actionTemplate.registerClickListener(async (actionId) => {
        const actionDetails = await getAction(actionId);
        this.renderDetailModalCallback(actionDetails);
      });
      container.appendChild(actionElement);
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

export default ActionsContent;
