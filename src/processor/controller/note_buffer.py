# this will be a sort of a base class for storing a note's processing
# state.

from src import db


class NoteProcessBuffer:
    def __init__(self, note: db.Note):
        self.note: db.Note = note
        self.category: db.Category | None = None
        self.annotation: db.Annotation | None = None
        self.action: db.Action | None = None
        self.todo: db.Todo | None = None
        self.command: db.Command | None = None

