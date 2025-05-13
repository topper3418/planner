import { getCuriosities, getCuriosityById } from "./curiosities";
import CuriosityTemplate from "./curiositiesTemplate";

class CuriositiesContent {
  constructor() {
    this.elements = {
      container: document.getElementById("curiosities-content"),
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
    const curiosities = await getCuriosities(filters);
    this.renderCuriosities(curiosities);
  }

  renderCuriosities(curiosities) {
    const container = this.elements.container;
    container.innerHTML = ""; // Clear previous content
    curiosities.forEach((curiosity) => {
      const curiosityTemplate = new CuriosityTemplate();
      const curiosityElement = curiosityTemplate.render(curiosity);
      curiosityTemplate.registerClickListener(async (curiosityId) => {
        const curiosityDetails = await getCuriosityById(curiosityId);
        this.renderDetailModalCallback(curiosityDetails);
      });
      container.appendChild(curiosityElement);
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

export default CuriositiesContent;
