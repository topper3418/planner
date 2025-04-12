from typing import List
from src import db

def bulk_upload_notes_list(notes: List[tuple]) -> List[db.Note]:
    """
    Bulk upload notes to the database.
    """
    created_notes = []
    for timestamp, note_text in notes:
        note = db.Note.create(
            note_text,
            timestamp=timestamp,
        )
        created_notes.append(note)
    return created_notes
