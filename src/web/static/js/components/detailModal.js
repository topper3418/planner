class DetailModal {
  constructor() {
    this.elements = {
      containers: {
        modal: document.getElementById("detail-modal"),
      },
      buttons: {
        openButton: document.getElementById("detail-modal-button"),
        closeButton: document.getElementById("detail-modal-close-button"),
      },
      content: document.getElementById("detail-modal-content"),
    };
    this.setContent = this.setContent.bind(this);
    this.open = this.open.bind(this);
    this.close = this.close.bind(this);
  }

  open() {
    this.elements.containers.modal.classList.remove("hidden");
    this.elements.content.innerHTML = "<p>Loading...</p>";
  }

  close() {
    this.elements.containers.modal.classList.add("hidden");
  }

  setContent(contentJSON) {
    this.elements.content.innerHTML = `<pre>${JSON.stringify(contentJSON, null, 2)}</pre>`;
  }
}

export default DetailModal;
