class DataModal {
  constructor() {
    this.elements = {
      modal: document.getElementById("data-modal"),
      closeButton: document.getElementById("data-modal-close-button"),
      content: document.getElementById("data-modal-content"),
    };
    this.setContent = this.setContent.bind(this);
    this.open = this.open.bind(this);
    this.close = this.close.bind(this);
    this.elements.closeButton.addEventListener("click", this.close);
  }

  open() {
    this.elements.modal.classList.remove("hidden");
    this.elements.content.innerHTML = "<p>Loading...</p>";
  }

  close() {
    this.elements.modal.classList.add("hidden");
  }

  setContent(contentJSON) {
    this.open();
    console.log("elements", this.elements);
    this.elements.content.innerHTML = `<pre>${JSON.stringify(contentJSON, null, 2)}</pre>`;
  }
}

export default DataModal;
