from typing import Optional

from openai.types.responses import FunctionToolParam
from ..db import Action, Todo
from ..util import parse_time


def update_action(
        action_id: int,
        action_text: Optional[str] = None,
        timestamp: Optional[str] = None,
        todo_id: Optional[int] = None,
        mark_complete: Optional[bool] = None,
) -> Action:
    """
    Update an action with the processed action text.
    """
    # Get the action
    action = Action.get_by_id(action_id)
    if action is None:
        raise ValueError(f"Action with id {action_id} not found")
    # Update the action
    if action_text is not None:
        action.action_text = action_text
    if timestamp is not None:
        action.timestamp = parse_time(timestamp)
    if todo_id is not None:
        action.todo_id = todo_id
        if mark_complete is not None:
            action.mark_complete = mark_complete
            if mark_complete:
                todo = Todo.get_by_id(todo_id)
                if todo is None:
                    raise ValueError(f"Todo with id {todo_id} not found")
                todo.complete = True
                todo.save()
    action.save()
    return action


def get_update_action_tool() -> FunctionToolParam:
    return FunctionToolParam(
        name="update_action",
        description="Update an action from a user command. The user should make their intent obvious in order for this function to be called. Only update the fields that the user has specified",
        type="function",
        parameters={
            "type": "object",
            "properties": {
                "action_id": {
                    "type": "integer",
                    "description": "The ID of the action to update.",
                },
                "action_text": {
                    "type": "string",
                    "description": "The text of the action.",
                },
                "timestamp": {
                    "type": "string",
                    "description": "The timestamp of the action.",
                },
                "todo_id": {
                    "type": "integer",
                    "description": "The ID of the todo that the action is acting upon.",
                },
                "mark_complete": {
                    "type": "boolean",
                    "description": "Whether the action completes the todo",
                },
            },
            'required': ['action_id'],
            "additionalProperties": False,
        },
        strict=False,
    )
