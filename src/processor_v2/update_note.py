from typing import Optional
from openai.types.responses import FunctionToolParam
from ..db import Note


def update_note(note_id: int, note_text: Optional[str], processed_note_text: Optional[str]) -> Optional[Note]:
    note = Note.get_by_id(note_id)
    if note is None:
        return None
    note.note_text = note_text or "";
    note.processed_note_text = processed_note_text or "";
    note.processed = False
    note.save()
    return note


def get_update_note_tool() -> FunctionToolParam:
    return FunctionToolParam(
        name="update_note",
        description="Update a note with the processed note text. The user should make their intent obvious in order for this function to be called",
        type="function",
        parameters={
            "type": "object",
            "properties": {
                "note_id": {
                    "type": "integer",
                    "description": "The ID of the note to update.",
                },
                "processed_note_text": {
                    "type": "string",
                    "description": "A new way to have",
                },
            },
            "required": ["note_id", "note_text"],
        },
        strict=True,
    )
