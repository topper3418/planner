// notebookClient.js

/**
 * Gets the current notebook name.
 * @returns {Promise<string>} The current notebook name.
 */
export async function getCurrentNotebook() {
  const response = await fetch("/api/notebook", {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching current notebook:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched current notebook:", data);
  }
  return data.notebook;
}

/**
 * Gets a list of all available notebooks.
 * @returns {Promise<string[]>} Array of notebook names.
 */
export async function getAllNotebooks() {
  const response = await fetch("/api/notebooks", {
    headers: { "Content-Type": "application/json" },
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error fetching notebooks:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Fetched notebooks:", data);
  }
  return data.notebooks;
}

/**
 * Sets the current notebook, creating it if it doesn't exist.
 * @param {string} notebook - The name of the notebook to set.
 * @returns {Promise<string>} The name of the set notebook.
 */
export async function setNotebook(notebook) {
  if (!notebook) {
    throw new Error("Notebook name is required");
  }
  const response = await fetch("/api/notebook", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notebook }),
  });
  const data = await response.json();
  if (data.error) {
    console.error("Error setting notebook:", data.error);
    throw new Error(data.error);
  } else {
    console.log("Set notebook:", data);
  }
  return data.notebook;
}
