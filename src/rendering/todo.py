from typing import List
from datetime import datetime

from termcolor import colored

from ..db import Todo, Action
from ..util import format_time


def strf_todo(todo: Todo) -> str:
    # create the text
    checkbox_inner = (
        "X" if todo.complete else "O" if todo.cancelled else " "
    )
    pretty_text = f"[{checkbox_inner}] [{str(todo.id).rjust(4, '0')}]: {todo.todo_text}"
    if todo.target_start_time and todo.target_end_time:
        pretty_text += (
            f"\n    {todo.target_start_time} -> {todo.target_end_time}"
        )
    elif todo.target_start_time:
        pretty_text += f"\n    {todo.target_start_time} -> *"
    elif todo.target_end_time:
        pretty_text += f"\n    * -> {todo.target_end_time}"
    created = todo.source_note.timestamp
    pretty_text += f"\n    Created: {format_time(created)}"
    if todo.complete:
        # gotta find the completed time
        complete_action = Action.get_by_todo_complete(todo.id)
        if complete_action:
            pretty_text += f"\n    Completed: {format_time(todo.source_note.timestamp)}"
        # TODO: add cancelled time if applicable
    now = datetime.now()
    # color the text based on status
    # lets just do this in english, simpler that way
    start_time = todo.target_start_time
    started = start_time < now if start_time else False
    end_time = todo.target_end_time
    late = end_time < now if end_time else False
    # yellow if it's started and not yet late
    yellow = started and not late
    # red if it's late
    red = late
    # green if it's complete
    green = todo.complete
    # grey if it's cancelled
    grey = todo.cancelled
    # white if no time given
    white = not started and not end_time
    # now in order of priority...
    if green:
        pretty_text = colored(pretty_text, "green")
    elif grey:
        pretty_text = colored(pretty_text, "light_grey")
    elif red:
        pretty_text = colored(pretty_text, "red")
    elif yellow:
        pretty_text = colored(pretty_text, "yellow")
    elif white:
        pretty_text = colored(pretty_text, "white")
    else:
        print("todo is not anything")
        pretty_text = colored(pretty_text, "magenta")
    return pretty_text


def strf_todo_light(todo: Todo) -> str:
    return f"{todo.id} - {todo.target_start_time} - {todo.target_end_time} - {todo.todo_text}"


def strf_todos(todos: List[Todo]) -> str:
    """
    Pretty prints a todo like:

    [ ] 1: todo-text - 2023-04-12 06:00:00 - 2023-04-12 06:00:00
    """
    if not todos:
        return "No todos found"
    pretty_todos = ""
    for todo in todos:
        pretty_text = strf_todo(todo)
        pretty_todos += pretty_text + "\n"
    return pretty_todos


def json_todo(todo: Todo) -> dict:
    """
    Converts a todo to a json object
    """
    # extract props for cleanliness
    note = todo.source_note
    parent = todo.parent
    children = todo.children
    # attach the related objects to the json
    output_json = {}
    output_json["todo"] = todo.model_dump()
    output_json["note"] = note.model_dump() if note else None
    output_json["parent"] = parent.model_dump() if parent else None
    output_json["children"] = [child.model_dump() for child in children]
    return output_json
