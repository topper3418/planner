# this  module will support the ability to take items from the database
# and convert them to text for printing. 
# this will sort of be like parameterized view getting.
from typing import List
from datetime import datetime

from termcolor import colored

from . import db


def banner(text: str, width: int = 75) -> str:
    """
    returns a banner like this
    =================================================================
    ||                           BANNER                            ||
    =================================================================
    """
    top = "=" * width
    side = "||"
    text = text.center(width - len(side) * 2)
    return f"{top}\n{side}{text}{side}\n{top}"



def strf_notes(notes: List[db.Note], show_processed_text: bool = False) -> str:
    """
    Pretty prints a note like: 

    2023-04-12 06:00:00 - action
        Woke up and rolled out of bed.
    ---------------------------------------------------------------------------
    """
    pretty_notes = "" 
    for note in notes:
        annotation = db.Annotation.get_by_note_id(note.id)
        if annotation is None:
            category_name = "Uncategorized"
            color = "white"
        else:
            category_name = annotation.category.name
            color = annotation.category.color
        if show_processed_text and note.processed_note_text:
            note_text = note.processed_note_text
        else:
            note_text = note.note_text
        cololred_category = colored(category_name, color)
        pretty_text = f"{note.timestamp} - {cololred_category}\n"
        # we have to account for the tab character in the text
        space = 75 - 8
        if len(note_text) > space:
            pretty_text += "\t" + note_text[:space] + "\n"
            remainder = note.note_text[space:]
            while remainder:
                if len(remainder) > space:
                    pretty_text += "\t" + remainder[:space] + "\n"
                    remainder = remainder[space:]
                else:
                    pretty_text += "\t" + remainder + "\n"
                    remainder = ""
        else:
            pretty_text += "\t" + note_text + "\n"
        pretty_notes += pretty_text + "-" * 75 + "\n" 
    return pretty_notes


def strf_todos(todos: List[db.Todo]) -> str:
    """
    Pretty prints a todo like: 

    [ ] 1: todo-text - 2023-04-12 06:00:00 - 2023-04-12 06:00:00
    """
    pretty_todos = ""
    for todo in todos:
        annotation = todo.source_annotation
        pretty_text = f"[{'X' if todo.complete else " "}]{todo.id}: {todo.todo_text} - {todo.target_start_time} - {todo.target_end_time}"        
        now = datetime.now()
        if todo.complete:
            pretty_text = colored(pretty_text, "green")
        elif todo.target_start_time and datetime.strptime(todo.target_start_time, "%Y-%m-%d %H:%M:%S") < now:
            pretty_text = colored(pretty_text, "yellow")
        elif todo.target_end_time and datetime.strptime(todo.target_end_time, "%Y-%m-%d %H:%M:%S") < now:
            pretty_text = colored(pretty_text, "red")
        else:
            pretty_text = colored(pretty_text, "white")
        pretty_todos += pretty_text + "\n"
    return pretty_todos


def strf_actions(actions: List[db.Action]) -> str:
    """
    Pretty prints an action like: 

    2023-04-12 06:00:00 - 2023-04-12 06:00:00
        action-text
    """
    pretty_actions = ""
    for action in actions:
        if action.todo_id:
            todo = db.Todo.get_by_id(action.todo_id)
            if todo:
                action_text = f"{action.action_text} -> {todo.todo_text}"
            else:
                action_text = action.action_text
            if action.mark_complete:
                action_text = colored(action_text, "green")
        else:
            action_text = action.action_text
        pretty_text = f"{action.start_time} - {action.end_time}\n\t{action_text}"
        pretty_actions += pretty_text + "\n" + "-" * 75 + "\n"     
    return pretty_actions


def strf_curiosities(curiosities: List[db.Annotation]) -> str:
    """
    Pretty prints an observation like: 

    2023-04-12
    original-note
        observation-text
    """
    pretty_curiosities = ""
    for curiosity in curiosities:
        pretty_text = f"{curiosity.note.timestamp}\n{curiosity.note.note_text}\n\t{curiosity.annotation_text}"
        pretty_curiosities += pretty_text + "-" * 75 + "\n"
    return pretty_curiosities


