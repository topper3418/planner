import { getCurrentNotebook } from "../client/notebooks.js";

class Header {
  constructor() {
    this.elements = {
      title: document.getElementById("header-title"),
    };
  }

  async setTitle() {
    const activeNotebook = await getCurrentNotebook();
    if (activeNotebook) {
      this.elements.title.textContent = activeNotebook;
    } else {
      this.elements.title.textContent = "No active notebook";
    }
  }
}

export default Header;
