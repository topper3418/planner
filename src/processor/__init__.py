import logging

from .. import db
from .categorizor import categorize_note
from .annotator import annotate_note
from .create_action import create_action
from .create_todo import create_todo
from .create_command import create_command

logger = logging.getLogger(__name__) 


class NoteProcessor:
    """
    Object that is initialized with a note, and processes said note according to a sequence. 
    Supports injection of objects for the sake of skipping initial steps in the case of a re-process. 
    """
    def __init__(self, note: db.Note):
        self.note = note
        self.category: db.Category | None = None
        self.annotation: db.Annotation | None = None
        self.action: db.Action | None = None
        self.todo: db.Todo | None = None
        self.command: db.Command | None = None

    def process(self):
        # Here you would process the note (e.g., send it to OpenAI)
        # For demonstration, we'll just print it
        logger.info(f"Processing note: {self.note.note_text}")
        # Categorize the note
        if self.category is None:
            category = categorize_note(self.note)
            if category is None:
                logger.error(f"Failed to categorize note: {self.note.note_text}")
                return None
            self.category = category
        # Annotate the note
        if self.annotation is None:
            annotation = annotate_note(self.note, self.category)
            if annotation is None:
                logger.error(f"Failed to annotate note: {self.note.note_text}")
                self.note.processing_error = "Failed to annotate"  # Mark as failed, in case of failure
                self.note.save()
                return None
            annotation.note = self.note
            annotation.category = self.category
            self.annotation = annotation
        # some categories require further processing. 
        # curiosities and observations do not at this time.
        # if it is an action, create an action in the database
        if self.category.name == "action":
            action = create_action(self.annotation)
            if action is None:
                logger.error(f"Failed to create action: {self.annotation.annotation_text}")
                self.note.processing_error = "Failed to create action"
            self.action = action
        # if it is a todo, create a todo in the database
        elif self.category.name == "todo":
            todo = create_todo(self.annotation)
            if todo is None:
                logger.error(f"Failed to create todo: {self.annotation.annotation_text}")
                self.note.processing_error = "Failed to create todo"
            self.todo = todo
        # if it is a command, route the command
        elif self.category.name == "command":
            command = create_command(self.annotation)
            if command is None:
                logger.error(f"Failed to create command: {self.annotation.annotation_text}")
                self.note.processing_error = "Failed to create command"
            self.command = command
            # build the routing out here. will probably need a "controller module"


