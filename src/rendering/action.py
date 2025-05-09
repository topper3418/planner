from typing import List
from datetime import datetime

from termcolor import colored

from ..db import Todo, Action
from ..config import TIMESTAMP_FORMAT


def strf_action(action: Action) -> str:
    if action.todo_id:
        todo = Todo.get_by_id(action.todo_id)
        if todo:
            action_text = f"{action.action_text} -> {todo.todo_text}"
        else:
            action_text = action.action_text
        if action.mark_complete:
            action_text = colored(action_text, "green")
    else:
        action_text = action.action_text
    pretty_text = f"[{str(action.id).rjust(4, '0')}] {datetime.strftime(action.timestamp, TIMESTAMP_FORMAT)}\n\t{action_text}"
    return pretty_text


def strf_action_light(action: Action) -> str:
    action_str = f"{action.id} - {action.timestamp} - {action.action_text}"
    if action.todo and action.mark_complete:
        action_str += f" -> {action.todo.todo_text} (completed)"
    elif action.todo:
        action_str += f" -> {action.todo.todo_text}"
    return action_str


def strf_actions(actions: List[Action]) -> str:
    """
    Pretty prints an action like:

    2023-04-12 06:00:00 - 2023-04-12 06:00:00
        action-text
    """
    if not actions:
        return "No actions found"
    pretty_actions = ""
    for action in actions:
        pretty_text = strf_action(action)
        pretty_actions += pretty_text + "\n" + "-" * 75 + "\n"
    return pretty_actions


def json_action(action: Action) -> dict:
    """
    Converts an action to a json object
    """
    # find the related objects
    todo = action.todo
    note = action.source_note
    # attach the related objects to the json
    output_json = {}
    output_json["action"] = action.model_dump()
    output_json["todo"] = todo.model_dump() if todo else None
    output_json["note"] = note.model_dump() if note else None
    return output_json
