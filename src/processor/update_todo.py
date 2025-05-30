from typing import Optional

from openai.types.responses import FunctionToolParam

from src.errors import ProcessUpdateError, SaveDBObjectError
from ..db import Action, Todo
from ..util import parse_time


def update_todo(
    todo_id: int,
    todo_text: Optional[str] = None,
    target_start_time: Optional[str] = None,
    target_end_time: Optional[str] = None,
    parent_id: Optional[int] = None,
    complete: Optional[bool] = None,
    cancelled: Optional[bool] = None,
) -> Todo:
    """
    Update a todo with the processed todo text.
    """
    # Get the todo
    todo = Todo.get_by_id(todo_id)
    if todo is None:
        raise ValueError(f"Todo with id {todo_id} not found")
    # Update the todo
    if todo_text:
        todo.todo_text = todo_text
    if target_start_time:
        todo.target_start_time = parse_time(target_start_time)
    if target_end_time:
        todo.target_end_time = parse_time(target_end_time)
    if parent_id:
        todo.parent_id = parent_id
    if complete is not None:
        todo.complete = complete
    if cancelled is not None:
        todo.cancelled = cancelled
    try:
        todo.save()
    except SaveDBObjectError as e:
        raise ProcessUpdateError(f"Error saving todo: {e}")
    return todo


def get_update_todo_tool() -> FunctionToolParam:
    return FunctionToolParam(
        name="update_todo",
        description="Update a todo from a user command. The user should make their intent obvious in order for this function to be called. Only update the fields that the user has specified",
        type="function",
        parameters={
            "type": "object",
            "properties": {
                "todo_id": {
                    "type": "integer",
                    "description": "The ID of the todo to update.",
                },
                "todo_text": {
                    "type": "string",
                    "description": "The text of the todo. The user wants to update what the todo says.",
                },
                "target_start_time": {
                    "type": "string",
                    "description": "The target start time of the todo. the user wants to update when they intend to start the task",
                },
                "target_end_time": {
                    "type": "string",
                    "description": "The target end time of the todo. the user wants to update when the intend (or need) to have the task finished by",
                },
                "parent_id": {
                    "type": "integer",
                    "description": "The ID of the parent todo. the user wants to change which todo this appears under in the todo tree",
                },
                "complete": {
                    "type": "boolean",
                    "description": "Whether the todo is complete. The todo either wants to mark it complete if its marked incomplete, or mark it incomplete if its marked complete.",
                },
                "cancelled": {
                    "type": "boolean",
                    "description": "Whether the todo is cancelled. The todo either wants to mark it cancelled if its marked incomplete, or mark it incomplete if its marked complete.",
                },
            },
            "required": [
                "todo_id",
                "todo_text",
                "target_start_time",
                "target_end_time",
                "parent_id",
                "complete",
                "cancelled",
            ],
            "additionalProperties": False,
        },
        strict=True,
    )
