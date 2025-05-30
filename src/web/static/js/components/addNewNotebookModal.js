import { createNotebook } from "../client/notebooks.js";

class AddNewNotebookModal {
  constructor() {
    this.elements = {
      modal: document.getElementById("add-new-notebook-modal"),
      content: document.getElementById("add-new-notebook-content"),
      input: document.getElementById("add-new-notebook-name-input"),
      openButton: document.getElementById("add-new-notebook-open-button"),
      submitButton: document.getElementById("add-new-notebook-submit-button"),
    };
    console.log("AddNewNotebookModal elements:", this.elements);
    this.elements.openButton.addEventListener("click", () => this.open());
    this.elements.submitButton.addEventListener("click", () => this.submit());
    document.addEventListener("click", (event) => {
      if (
        !this.elements.content.contains(event.target) &&
        !this.elements.openButton.contains(event.target)
      ) {
        this.close();
      }
    });
  }

  async open() {
    this.elements.modal.classList.remove("hidden");
  }

  close() {
    this.elements.modal.classList.add("hidden");
  }

  async submit() {
    console.log("Submitting new notebook modal");
    const notebookName = this.elements.input.value.trim();
    console.log("Submitting new notebook", notebookName);
    if (!notebookName) {
      alert("Please enter a notebook name");
      return;
    }
    try {
      const response = await createNotebook(notebookName);
      this.close();
    } catch (error) {
      console.error("Error creating notebook:", error);
      alert(`Error creating notebook: ${error.message}`);
    }
  }
}

export default AddNewNotebookModal;
