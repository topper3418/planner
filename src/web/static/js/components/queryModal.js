class QueryModal {
  constructor() {
    this.elements = {
      containers: {
        modal: document.getElementById("query-modal"),
      },
      input: {
        query: document.getElementById("query-input"),
      },
      response: document.getElementById("query-response"),
      buttons: {
        openButton: document.getElementById("query-modal-button"),
        closeButton: document.getElementById("modal-close-button"),
        submitButton: document.getElementById("query-submit-button"),
      },
    };
    this.registerClickListeners();
  }

  open() {
    this.elements.containers.modal.classList.remove("hidden");
    this.elements.input.query.focus();
  }

  close() {
    this.elements.containers.modal.classList.add("hidden");
  }

  registerClickListeners() {
    this.elements.buttons.openButton.addEventListener("click", () => {
      this.open();
    });
    this.elements.buttons.closeButton.addEventListener("click", () => {
      this.close();
    });
  }

  registerSubmitCallback(callback) {
    this.elements.buttons.submitButton.addEventListener("click", async () => {
      const query = this.elements.input.query.value.trim();
      if (!query) {
        this.elements.response.innerHTML =
          '<p class="text-red-500">Please enter a query</p>';
        return;
      }
      this.elements.response.innerHTML = "<p>Processing query...</p>";
      const response = await callback(query);
      if (response.error) {
        this.elements.response.innerHTML = `<p class="text-red-500">Error: ${response.error}</p>`;
      } else {
        const paragraphs = response.summary
          .map((paragraph) => `<p>${paragraph}</p>`)
          .join("");
        this.elements.response.innerHTML = `<h3>Response:</h3>${paragraphs}`;
      }
    });
  }
}
