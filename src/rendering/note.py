from typing import List

from src.db.command import Command
from ..db import Note, Annotation, Action, Todo
from ..util import format_time, format_paragraph

from termcolor import colored

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


def strf_note_light(note: Note) -> str:
    return f"{note.id} - {note.timestamp} - {note.processed_note_text}"


def strf_notes(notes: List[Note], show_processed_text: bool = False) -> str:
    """
    Pretty prints a note like: 

    2023-04-12 06:00:00 - action
        Woke up and rolled out of bed.
    ---------------------------------------------------------------------------
    """
    if not notes:
        return "No notes found"
    pretty_notes = "" 
    for note in notes:
        pretty_text = strf_note(note, show_processed_text)
        pretty_notes += pretty_text + "-" * 75 + "\n" 
    return pretty_notes


def json_note(note: Note) -> dict:
    """
    Converts a note to a json object
    """
    output_json = {}
    output_json["note"] = note.model_dump()
    annotation = Annotation.get_by_note_id(note.id)
    # find the related objects
    todo = Todo.get_by_source_annotation_id(note.id)
    action = Action.get_by_source_annotation_id(annotation.id) if annotation else None
    command = Command.get_by_source_annotation_id(annotation.id) if annotation else None
    output_json["annotation"] = annotation.model_dump() if annotation else None
    output_json["todo"] = todo.model_dump() if todo else None
    output_json["action"] = action.model_dump() if action else None
    output_json["command"] = command.model_dump() if command else None
    return output_json
