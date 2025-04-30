import logging
from typing import List, Optional

from openai.types.responses import ToolParam



from ..config import TIMESTAMP_FORMAT
from ..db import Note, Annotation, Action, Todo
from ..util import NL

from .find_todo import find_todo

logger = logging.getLogger(__name__)


def create_todo(
        note: Note,
        todo_text: str,
        target_start_time: Optional[str] = None,
        target_end_time: Optional[str] = None,
        parent_id: Optional[int] = None,
) -> Todo:
    # if a todo id of 0 is given, return all todos from the past three months and try again.
    todo = Todo.create(
        todo_text=todo_text,
        target_start_time=target_start_time,
        target_end_time=target_end_time,
        source_note_id=note.id,
    )
    if parent_id == 0:
        todo_response = find_todo(todo)
        if todo_response is not None:
            todo, _ = todo_response
            todo.parent_id = todo.id
            todo.save()
    elif parent_id:
        # if a todo id is given, attach it to the action
        todo.parent_id = parent_id
        todo.save()
    return todo


def get_create_todo_tool() -> ToolParam:
    return {
        "type": "function",
        "name": "create_todo",
        "description": "Create a todo, when the user mentions something they need to do but are not intending to do right away.",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_text": {
                    "type": "string",
                    "description": "Text of the todo. It should read like a todo list",
                },
                "target_start_time": {
                    "type": "string",
                    "description": f"Timestamp of the todo. It should conform to the format {TIMESTAMP_FORMAT}. If specified, use the time given in the note. This is relevant when the user mentions what time they want to start a task. I need to do this at noon. Tomorrow at this time I have to do that. Use the current time of the note to extrapolate to a best guess for time."
                },
                "target_end_time": {
                    "type": "string",
                    "description": f"Timestamp of the todo. It should conform to the format {TIMESTAMP_FORMAT}. If specified, use the time given in the note. This is relevant when the user mentions what time they want to finish a task. I need to have this done by noon. I need to have that done by tomorrow at 3. Use the current time of the note to extrapolate to a best guess for time."
                },
                "parent_id": {
                    "type": "integer",
                    "description": "ID of the parent todo. This is relevant when the user mentions a task that is part of a larger task. I need to do this in order to do that. When I am doing this task I should also do that task. The parent task is the one that depends on the child task, so for this param give the value of the task that depends on this newly created task. If it seems like the user was trying to reference a task that was not listed, then return 0 and additional todos will be provided.",
                },
            },
            "required": ['todo_text'],
        }
    }


