import { getNotes, getNoteById, createNote } from "./notes.js";
import { getTodos, getTodoById } from "./todos";
import { getActions, getActionById } from "./actions";
import { submitQuery } from "./query";
import { getCurrentNotebook, setNotebook, getAllNotebooks } from "./notebooks";

export default {
  getNotes,
  getNoteById,
  createNote,
  getTodos,
  getTodoById,
  getActions,
  getActionById,
  submitQuery,
  getCurrentNotebook,
  setNotebook,
  getAllNotebooks,
};
