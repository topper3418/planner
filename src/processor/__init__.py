import logging

from .. import db
from .categorizor import categorize_note
from .annotator import annotate_note
from .create_action import create_action
from .create_todo import create_todo
from .create_command import create_command

logger = logging.getLogger(__name__) 





def process_unprocessed_note(note: db.Note):
    # Here you would process the note (e.g., send it to OpenAI)
    # For demonstration, we'll just print it
    logger.info(f"Processing note: {note.note_text}")
    # Categorize the note
    category = categorize_note(note)
    if category is None:
        logger.error(f"Failed to categorize note: {note.note_text}")
        return None
    # Annotate the note
    annotation = annotate_note(note, category)
    if annotation is None:
        logger.error(f"Failed to annotate note: {note.note_text}")
        note.processing_error = "Failed to annotate"  # Mark as failed, in case of failure
        note.save()
        return None
    # some categories require further processing. 
    # curiosities and observations do not at this time.
    if category.name in ["action", "todo", "command"]:
        annotation.note = note
        annotation.category = category
    # if it is an action, create an action in the database
    if category.name == "action":
        action = create_action(annotation)
        if action is None:
            logger.error(f"Failed to create action: {annotation.annotation_text}")
            note.processing_error = "Failed to create action"
    # if it is a todo, create a todo in the database
    elif category.name == "todo":
        todo = create_todo(annotation)
        if todo is None:
            logger.error(f"Failed to create todo: {annotation.annotation_text}")
            note.processing_error = "Failed to create todo"
    # if it is a command, route the command
    elif category.name == "command":
        command = create_command(annotation)
        if command is None:
            logger.error(f"Failed to create command: {annotation.annotation_text}")
            note.processing_error = "Failed to create command"
        # build the routing out here. will probably need a "controller module"
    
    return note


