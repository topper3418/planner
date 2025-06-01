import { getNotes, getNoteById, createNote } from "./notes.js";
import { getTodos, getTodoById } from "./todos.js";
import { getActions, getActionById } from "./actions.js";
import { submitQuery } from "./query.js";
import {
  getCurrentNotebook,
  setNotebook,
  getAllNotebooks,
} from "./notebooks.js";

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
