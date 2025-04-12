from src import db

from .note_buffer import NoteProcessBuffer
from .unprocess_note import unprocess_note


def route_command(command: db.Command) -> NoteProcessBuffer:
    """
    Routes the command to the appropriate function based on its type.
    """

    if command.command_text == "update_note_text":
        # update the note text
        note = db.Note.get_by_id(command.target_id)
        if not note:
            raise ValueError(f"Note with ID {command.target_id} not found")
        note.note_text = command.desired_value
        note.save()
        unprocess_note(note)
        buffer = NoteProcessBuffer(note)
        return buffer
    if command.command_text == "update_note_category":
        # update the note category
        note = db.Note.get_by_id(command.target_id)
        if not note:
            raise ValueError(f"Note with ID {command.target_id} not found")
        buffer = NoteProcessBuffer(note)
        category = db.Category.find_by_name(command.desired_value)
        if not category:
            raise ValueError(f"Category with name {command.desired_value} not found")
        buffer.category = category
        # get the annotation
        annotation = db.Annotation.get_by_id(command.source_annotation_id)
        if not annotation:
            raise ValueError(f"Annotation with ID {command.source_annotation_id} not found")
        # remove objects that might have been created, depending on the category
        if annotation.category.name == "command":
            # commands cannot be undone
            raise ValueError("Commands cannot be undone")
        # update the category
        annotation.category = category
        annotation.reprocess = True
        annotation.save()
        buffer.annotation = annotation
        return buffer
