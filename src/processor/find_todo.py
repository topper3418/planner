import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from openai.types.responses import FunctionToolParam, ToolParam

from ..db import Command, Action, Todo  
from ..llm import get_light_client
from ..rendering import strf_todo_light
from ..util import NL

logger = logging.getLogger(__name__)


def find_todo(input_obj: Command | Action | Todo, exclude_todo_id: Optional[int] = None) -> Optional[Tuple[Todo, bool]]:
    client = get_light_client()
    one_month_ago = datetime.now() - timedelta(days=30)
    todos = Todo.get_all(after=one_month_ago)
    # filter out the todo with the exclude_todo_id
    if exclude_todo_id is not None:
        todos = [todo for todo in todos if todo.id != exclude_todo_id]
    tools: List[ToolParam] = [get_find_todo_tool(todos)]
    tool_response_json = client.responses.create(
        model="gpt-4.1",
        instructions=f"""You are a master notetaking assistant. Your assignment is to match a command, action or child task to a todo.

        For your context, here are the todos from the past month:

        {NL.join(strf_todo_light(todo) for todo in todos)}""",
        input=input_obj.model_dump_json(),
        tools=tools
    )
    # get the first tool response
    if len(tool_response_json.output) == 0:
        return None 
    tool_response = tool_response_json.output[0]
    tool_response_json = tool_response.model_dump()
    args = tool_response_json.get("arguments")
    if args is None:
        logger.warning("Tool response did not contain arguments.")
        return None
    args = json.loads(args)
    todo_id = args.get("todo_id")
    if todo_id is None:
        return None
    todo = Todo.get_by_id(todo_id)
    if todo is None:
        logger.warning("Todo with ID %s not found in the database.", todo_id)
        return None
    mark_complete = args.get("mark_complete")
    if mark_complete is None:
        mark_complete = False
    return todo, mark_complete


def get_find_todo_tool(todos: List[Todo]) -> ToolParam:
    return FunctionToolParam(
        type="function",
        name="find_todo",
        description=f"""Match a todo to a user action, command or subtask
         - if it is an action being given indicate whether or not the action marks the todo complete. 
         - If the user input specifies a todo by its id, use that ID. Otherwise, infer the todo from the action or command. 
         - The user will try be clear, so don't go too far out on a limb. If the todo it is supposed to match is not clear, just return nothing
         - for marking complete, infer the todo's workflow and work out where that action would take place in the workflow. For example, if they are arriving home from doing something, where that something was an errand, it is complete. if the user says that a task is done, mark complete. if they say they are starting on a task, do not mark complete. if the todo is to build a fence, and they say they put in fence posts, do not mark complete. if you have a todo x, and the user says they just did x and add a bunch of notes, that todo is still a mark complete.""",
        parameters={
            "type": "object",
            "properties": {
                "todo_id": {
                    "type": "integer",
                    "description": "The ID of the todo to match.",
                    "enum": [todo.id for todo in todos],
                },
                "mark_complete": {
                    "type": "boolean",
                    "description": "Whether to mark the todo as complete, as opposed to beginning or remarking on it. ",
                },
            },
            "required": ["todo_id"],
            "additionalProperties": False,
        },
        strict=False,
    )
    
