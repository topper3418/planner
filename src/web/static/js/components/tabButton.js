class TabButton {
  constructor(tabName) {
    this.tabname = tabName;
    this.button = document.getElementById(`${tabName}-button`);
    this.clicked = false;
    this.button.addEventListener("click", () => {
      this.handleClick();
    });
    this.clickCallback = null;
    // when user is tabbing around, load the content
    this.button.addEventListener("focus", () => {
      if (!this.clicked) {
        this.handleClick();
      }
    });
  }

  handleClick() {
    this.clickCallback(this.tabname);
    this.setActive();
  }

  setActive() {
    this.button.classList.remove("bg-white", "text-blue-500");
    this.button.classList.add("bg-blue-500", "text-white");
    this.button.setAttribute("aria-pressed", "true");
    this.clicked = true;
  }

  setInactive() {
    this.button.classList.remove("bg-blue-500", "text-white");
    this.button.classList.add("bg-white", "text-blue-500");
    this.button.setAttribute("aria-pressed", "false");
    this.clicked = false;
  }

  registerClickCallback(callback) {
    this.clickCallback = callback;
  }
}

export default TabButton;
