from typing import List, Optional

from openai.types.responses import FunctionToolParam, ToolParam


from ..config import TIMESTAMP_FORMAT
from ..db import Action, Todo, Note
from ..logging import get_logger

from .find_todo import find_todo

logger = get_logger(__name__, "processor.log")


def create_action(
    note: Note,
    action_text: str,
    action_timestamp: str,
    todo_id: Optional[int] = None,
    mark_complete: bool = False,
) -> Action:
    # if a todo id of 0 is given, return all todos from the past three months and try again.
    action = Action.create(
        timestamp=action_timestamp,
        action_text=action_text,
        source_note_id=note.id,
    )
    if todo_id == 0:
        todo_response = find_todo(action)
        if todo_response is None:
            return action
        todo, mark_complete = todo_response
        todo_id = todo.id
    elif todo_id:
        todo = Todo.get_by_id(todo_id)
        if todo is None:
            logger.warning(
                "Todo with ID %s not found in the database.", todo_id
            )
            return action
    else:
        return action
    action.todo_id = todo_id
    action.mark_complete = mark_complete
    todo.complete = mark_complete
    todo.save()
    action.save()
    return action


def get_create_action_tool(todos: List[Todo]) -> ToolParam:
    return FunctionToolParam(
        type="function",
        name="create_action",
        description="Create an action, derived from the user's note when applicable. For instance, if they indicate that they just did something, or are about to start doing something, that is an action. This function should be called once per action that the user logs. If they log no actions, no call. If they log multiple actions in one note, one action call per action.",
        parameters={
            "type": "object",
            "properties": {
                "action_text": {
                    "type": "string",
                    "description": "Text of the aciton. It should read like a logbook",
                },
                "action_timestamp": {
                    "type": "string",
                    "description": f"Timestamp of the action. It should conform to the format {TIMESTAMP_FORMAT}. If specified, use the time given in the note. Use the current time if not specified. If the time specified is in the past, (I did this yesterday, I did that two hours ago, etc), use the timestamp from the note and extrapolate to get a best guess. Do not drop any digits, always show trailing zero's",
                },
                "todo_id": {
                    "type": "integer",
                    "description": """ID of the todo associated with the action. 
                     - If specified, use this ID, but only if it appears in the list of todos. 
                     - If not specified but it appears this action affects a todo already on the list, try to find the todo based on the action text. 
                     - Do not get creative, the user should try to make it obvious if they are trying to match to a todo and they will log many actions that have nothing to do with their todo list.
                     - return a 0 if it appears the user is trying to match to a todo but it is not on the list.""",
                    "enum": [0] + [todo.id for todo in todos],
                },
                "mark_complete": {
                    "type": "boolean",
                    "description": "True if the action marks the todo as complete. This is only relevant if a todo_id is specified",
                },
            },
            "required": [
                "action_text",
                "action_timestamp",
                "todo_id",
                "mark_complete",
            ],
            "additionalProperties": False,
        },
        strict=True,
    )
