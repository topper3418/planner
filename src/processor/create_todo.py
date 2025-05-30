from typing import List, Optional

from openai.types.responses import FunctionToolParam

from ..config import TIMESTAMP_FORMAT
from ..errors import CreateDBObjectError, SaveDBObjectError
from ..db import Note, Todo
from ..logging import get_logger

from .find_todo import find_todo

logger = get_logger(__name__, "processor.log")


def create_todo(
    note: Note,
    todo_text: str,
    target_start_time: Optional[str] = None,
    target_end_time: Optional[str] = None,
    parent_id: Optional[int] = None,
) -> Optional[Todo]:
    # if a todo id of 0 is given, return all todos from the past three months and try again.
    try:
        todo = Todo.create(
            todo_text=todo_text,
            target_start_time=target_start_time,
            target_end_time=target_end_time,
            source_note_id=note.id,
        )
    except CreateDBObjectError as e:
        logger.error("Error creating todo: %s", e)
        note.processing_error = str(e)
        note.save()
        return None
    if parent_id == 0:
        todo_response = find_todo(
            todo, exclude_todo_id=todo.id, include_mark_complete=False
        )
        if todo_response is None:
            logger.warning("No parent todo found for todo %s", todo_text)
            return todo
        found_todo, _ = todo_response
        parent_id = found_todo.id
    elif not parent_id:
        return todo
    # ensure the parent todo is not the same as the child todo
    logger.info(f"doing parent check on todo: {todo} {parent_id}")
    todo.parent_id = parent_id
    try:
        todo.save()
    except SaveDBObjectError as e:
        logger.error("Error updating todo parent: %s", e)
        note.processing_error = str(e)
        note.save()
    return todo


def get_create_todo_tool(todos: List[Todo]) -> FunctionToolParam:
    return FunctionToolParam(
        type="function",
        name="create_todo",
        description="Create a todo, when the user mentions something they need to do but are not intending to do right away. If they say they need to do something or they plan to do something at a future time, that is a todo. If the user does not create a todo in their note, do not call this function. If they list off multiple todos in one note, one todo call per todo.",
        parameters={
            "type": "object",
            "properties": {
                "todo_text": {
                    "type": "string",
                    "description": "Text of the todo. It should read like a todo list",
                },
                "target_start_time": {
                    "type": "string",
                    "description": f"""Planned time for the start of the task. 
                     - It should conform to the format {TIMESTAMP_FORMAT}. 
                     - This is relevant when the user mentions what time they want to start a task. 
                       - I need to do this at noon. 
                       - Tomorrow at this time I have to do that. 
                     - Do not guess a start time if the user merely mentions what time something needs to be done by. 
                     - This is an optional field so return null unless the user specifies a start time.""",
                },
                "target_end_time": {
                    "type": "string",
                    "description": f"""Planned time for the end of the task. 
                     - It should conform to the format {TIMESTAMP_FORMAT}. 
                     - This is relevant when the user mentions what time they want to finish a task. 
                       - I need to have this done by noon. 
                       - I need to have that done by tomorrow at 3. 
                     - Do not guess a duration and add an end time when the user only states what time they want to start a task. 
                     - This is an optional field so return null unless the user specifies an end time.""",
                },
                "parent_id": {
                    "type": "integer",
                    "description": """ID of the parent todo. 
                     - This is relevant when the user mentions a task that is part of a larger task. 
                       - I need to do this in order to do that. 
                       - When I am doing this task I should also do that task. 
                     - The parent task is the one that depends on the child task, so for this param give the value of the task that depends on this newly created task. 
                     - If it seems like the user was trying to reference a task that was not listed, then return 0 and additional todos will be provided. 
                     - This is an optional field so return null if the user does not mention a parent task.""",
                    "enum": [0] + [todo.id for todo in todos],
                },
            },
            "required": [
                "todo_text",
                "target_start_time",
                "target_end_time",
                "parent_id",
            ],
            "additionalProperties": False,
        },
        strict=True,
    )
