# this  module will support the ability to take items from the database
# and convert them to text for printing. 
# this will sort of be like parameterized view getting.
from typing import List
from datetime import datetime

from termcolor import colored

from .db import Note, Action, Todo, Annotation
from .config import TIMESTAMP_FORMAT
from .util import format_time


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


def clear_terminal():
    print("\033[H\033[J")


def format_paragraph(text: str, width: int = 75, indents=1) -> str:
    """
    Formats a paragraph to fit within a given width.
    """
    space = width - 8 * indents
    pretty_text = ""
    if len(text) > space:
        pretty_text += "\t" * indents + text[:space] + "\n"
        remainder = text[space:]
        while remainder:
            if len(remainder) > space:
                pretty_text += "\t" * indents + remainder[:space] + "\n"
                remainder = remainder[space:]
            else:
                pretty_text += "\t" * indents + remainder + "\n"
                remainder = ""
    else:
        pretty_text += "\t" * indents + text + "\n"
    return pretty_text


def strf_note(note: Note, show_processed_text: bool = False) -> str:
    """
    Pretty prints a note like:
    2023-04-12 06:00:00 - action
        Woke up and rolled out of bed. if the note is too long, it will be wrapped t
        o fit within the width.
    """
    annotation = Annotation.get_by_note_id(note.id)
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
    colored_category = colored(category_name, color)
    pretty_text = f"[{str(note.id).rjust(4, '0')}] {format_time(note.timestamp)} - {colored_category}"
    if note.processing_error:
        pretty_text += colored(f"\nError: {note.processing_error}", "red")
    pretty_text += f"\n{format_paragraph(note_text, 75)}"
    # we have to account for the tab character in the text
    return pretty_text


def strf_notes(notes: List[Note], show_processed_text: bool = False) -> str:
    """
    Pretty prints a note like: 

    2023-04-12 06:00:00 - action
        Woke up and rolled out of bed.
    ---------------------------------------------------------------------------
    """
    pretty_notes = "" 
    for note in notes:
        pretty_text = strf_note(note, show_processed_text)
        pretty_notes += pretty_text + "-" * 75 + "\n" 
    return pretty_notes


def strf_todo(todo: Todo) -> str:
    # create the text
    checkbox_inner = "X" if todo.complete else "O" if todo.cancelled else " "
    pretty_text = f"[{checkbox_inner}]{todo.id}: {todo.todo_text}"
    if todo.target_start_time and todo.target_end_time:
        pretty_text += f"\n{todo.target_start_time} -> {todo.target_end_time}"
    elif todo.target_start_time:
        pretty_text += f"\n{todo.target_start_time} -> *"
    elif todo.target_end_time:
        pretty_text += f"\n* -> {todo.target_end_time}"
    created = todo.source_annotation.note.timestamp
    pretty_text += f"\nCreated: {format_time(created)}"
    if todo.complete:
        # gotta find the completed time
        complete_action = Action.get_by_todo_complete(todo.id)
        if complete_action:
            pretty_text += f"\nCompleted: {format_time(todo.source_annotation.note.timestamp)}"
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
        print('todo is not anything')
        pretty_text = colored(pretty_text, "magenta")
    return pretty_text



def strf_todos(todos: List[Todo]) -> str:
    """
    Pretty prints a todo like: 

    [ ] 1: todo-text - 2023-04-12 06:00:00 - 2023-04-12 06:00:00
    """
    pretty_todos = ""
    for todo in todos:
        pretty_text = strf_todo(todo)
        pretty_todos += pretty_text + "\n"
    return pretty_todos


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
    pretty_text = f"{datetime.strftime(action.start_time, TIMESTAMP_FORMAT)}\n\t{action_text}"
    return pretty_text



def strf_actions(actions: List[Action]) -> str:
    """
    Pretty prints an action like: 

    2023-04-12 06:00:00 - 2023-04-12 06:00:00
        action-text
    """
    pretty_actions = ""
    for action in actions:
        pretty_text = strf_action(action)
        pretty_actions += pretty_text + "\n" + "-" * 75 + "\n"     
    return pretty_actions


def strf_curiosity(curiosity: Annotation) -> str:
    pretty_text = f"{curiosity.note.timestamp}\n{format_paragraph(curiosity.note.note_text, indents=0)}\n{format_paragraph(curiosity.annotation_text)}"
    return pretty_text


def strf_curiosities(curiosities: List[Annotation]) -> str:
    """
    Pretty prints an observation like: 

    2023-04-12
    original-note
        observation-text
    """
    curiosities.reverse()
    pretty_curiosities = ""
    for curiosity in curiosities:
        pretty_text = strf_curiosity(curiosity)
        pretty_curiosities += pretty_text + "-" * 75 + "\n"
    return pretty_curiosities


