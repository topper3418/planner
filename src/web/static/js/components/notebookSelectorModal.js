import { getAllNotebooks, setNotebook } from "../client/notebooks.js";

class NotebookSelectorModal {
  constructor() {
    this.elements = {
      modal: document.getElementById("notebook-selector-modal"),
      list: document.getElementById("notebook-selector-list"),
      addNewButton: document.getElementById("notebook-selector-add-new-button"),
      openButton: document.getElementById("notebook-selector-open-button"),
    };
    this.elements.openButton.addEventListener("click", () => this.open());
    this.addNewButtonCallback = null;
    document.addEventListener("click", (event) => {
      if (
        !this.elements.modal.contains(event.target) &&
        !this.elements.openButton.contains(event.target)
      ) {
        this.close();
      }
    });
  }

  async setContent() {
    const notebooks = await getAllNotebooks();
    this.elements.list.innerHTML = ""; // Clear the list
    notebooks.forEach((notebook) => {
      const listItem = document.createElement("li");
      listItem.textContent = notebook;
      listItem.className = "cursor-pointer hover:bg-gray-200 p-2";
      listItem.addEventListener("click", async () => {
        await setNotebook(notebook);
        this.close();
      });
      this.elements.list.appendChild(listItem);
    });
  }

  async open() {
    console.log("Opening notebook selector modal", this.elements.modal);
    // position it ot the bottom of the dropdown button
    const buttonRect = this.elements.openButton.getBoundingClientRect();
    this.elements.modal.style.top = `${buttonRect.bottom + window.scrollY}px`;
    this.elements.modal.style.left = `${buttonRect.left + window.scrollX}px`;
    // set the content
    await this.setContent();
    // show it
    this.elements.modal.classList.remove("hidden");
    this.elements.list.focus();
  }

  close() {
    this.elements.modal.classList.add("hidden");
  }

  registerAddNewButtonCallback(callback) {
    this.addNewButtonCallback = callback;
    this.elements.addNewButton.addEventListener("click", () => {
      if (this.addNewButtonCallback) {
        this.addNewButtonCallback();
      } else {
        console.error("addNewButtonCallback is not set");
      }
    });
  }
}

export default NotebookSelectorModal;
