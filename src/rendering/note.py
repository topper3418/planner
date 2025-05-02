from typing import List

from ..db import Note
from ..util import format_time, format_paragraph

from termcolor import colored

def strf_note(note: Note, show_processed_text: bool = False) -> str:
    """
    Pretty prints a note like:
    2023-04-12 06:00:00 - action
        Woke up and rolled out of bed. if the note is too long, it will be wrapped t
        o fit within the width.
    """
    if show_processed_text and note.processed_note_text:
        note_text = note.processed_note_text
    else:
        note_text = note.note_text
    created_objects = ['todos', 'actions', 'commands', 'curiosities']
    created_object_counts = {key: len(getattr(note, key)) for key in created_objects}
    created_objects_strings = [f'{key}({created_object_counts[key]})' for key in created_objects]
    pretty_text = f"[{str(note.id).rjust(4, '0')}] {format_time(note.timestamp)} - {' '.join(created_objects_strings)}"
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
    # find the related objects
    output_json["annotation"] = note.annotation.model_dump() if note.annotation else None
    output_json["todos"] = [todo.model_dump() for todo in note.todos]
    output_json["actions"] = [action.model_dump() for action in note.actions]
    output_json["commands"] = [command.model_dump() for command in note.commands]
    return output_json


def json_note_light(note: Note) -> dict:
    """
    Converts a note to a json object
    """
    note_json = note.model_dump()
    # find the related objects
    note_json["num_todos"] = note.num_todos
    note_json["num_actions"] = note.num_actions
    return note_json
