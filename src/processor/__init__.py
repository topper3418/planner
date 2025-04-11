import logging

from .. import db
from .categorizor import categorize_note
from .annotator import annotate_note
from .create_action import create_action

logger = logging.getLogger(__name__) 





def process_unprocessed_note():
    note = db.Note.get_next_unprocessed_note()
    if note:
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
        # if it is a command, route the command
        
        return note
    else:
        print("No unprocessed notes found.")


# this is where I put the grok integration. 
# put your xai key in your own environment
# come up with a couple more tables to store shit in
# then go
