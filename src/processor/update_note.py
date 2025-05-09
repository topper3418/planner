from openai.types.responses import FunctionToolParam
from ..db import Note
from ..logging import get_logger


logger = get_logger(__name__)

# TODO:
# figure out if this is really necessary, or if just updating the derivative objects is enough


def update_note(note_id: int, note_text: str) -> Note:
    note = Note.get_by_id(note_id)
    if note is None:
        logger.error(f"Note with ID {note_id} not found in the database.")
        raise ValueError(
            f"Note with ID {note_id} not found in the database."
        )
    # reset the note
    note.note_text = note_text
    note.processed_note_text = ""
    note.processed = False
    # remove the derivatives
    for action in note.actions:
        action.delete()
    for todo in note.todos:
        todo.delete()
    for curiosity in note.curiosities:
        curiosity.delete()
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
                "note_text": {
                    "type": "string",
                    "description": "the raw text of the note",
                },
            },
            "required": ["note_id", "note_text"],
            "additionalProperties": False,
        },
        strict=True,
    )
