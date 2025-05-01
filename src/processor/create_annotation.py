import logging
from typing import Optional

from openai.types.responses import FunctionToolParam, ToolParam


from ..config import TIMESTAMP_FORMAT
from ..db import Note, Annotation

logger = logging.getLogger(__name__)


def create_annotation(
        note: Note, 
        annotation_text: str,
        processed_note_text: Optional[str],
) -> Annotation:
    """
    Annotate a note with a category.
    """

    # Create the annotation
    annotation = Annotation.create(
        note_id=note.id,
        annotation_text=annotation_text,
    )
    annotation.save()

    # update the processed note text
    note.processed_note_text = processed_note_text if processed_note_text else note.note_text
    note.save()

    return annotation

def get_create_annotation_tool() -> ToolParam:
    return FunctionToolParam(
        type="function",
        name="create_annotation",
        description="Clean up text for the note",
        parameters={
            "type": "object",
            "properties": {
                "annotation_text": {
                    "type": "string",
                    "description": f"Text of the annotation. This is the text that a future assistant will use to create summaries. Be verbose, but not creative. Always include the timing in full {TIMESTAMP_FORMAT} format, using the note's timestamp as a refence, as the summarizer will not have access to the timestamp. The only fleshing out of the note text should be if the note was vague and there is relevant context provided to flesh it out. For example 'I need to mow the lawn today' 'I need to pick weeds today' -> (later) 'i did the yardwork I had planned' -> 'the user mowed the lawn and picked weeds",
                },
                "processed_note_text": {
                    "type": "string",
                    "description": "Processed note text. Reword the note to be more concise and clear. Do not get creative, if it is already concise and clear and perfect you can leave this one out. Unlike the annotation text, this rewording should be from the perspective of the user",
                }
            },
            "required": ["annotation_text"],
            "additionalProperties": False,
        },
        strict=False,
    )
