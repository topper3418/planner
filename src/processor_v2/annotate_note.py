import logging

from openai.types.responses import ToolParam


from ..config import TIMESTAMP_FORMAT
from ..db import Note, Category, Annotation
from ..util import NL
from ..rendering import strf_category_light

logger = logging.getLogger(__name__)


def annotate_note(
        note: Note, 
        category_name: str, 
        annotation_text: str,
        processed_note_text: str,
) -> Annotation:
    """
    Annotate a note with a category.
    """
    # Ensure the category exists
    category = Category.get_by_name(category_name)
    if category is None:
        raise ValueError(f"Category '{category_name}' does not exist.")

    # Create the annotation
    annotation = Annotation.create(
        note_id=note.id,
        category_id=category.id,
        annotation_text=annotation_text,
    )
    annotation.save()

    # update the processed note text
    note.processed_note_text = processed_note_text
    note.save()

    return annotation

categories = Category.get_all()

def get_annotate_note_tool(categories) -> ToolParam:
    return {
        "type": "function",
        "name": "annotate_note",
        "description": f"""Annotate a note with a category and give a third person description of the note.
         - refer to the user as "the user"
         - choose the relevant category from the following list:
         {NL.join(strf_category_light(category) for category in categories)}
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "category_name": {
                    "type": "string",
                    "description": "Name of the category to use for annotation.",
                    "enum": [category.name for category in categories],
                },
                "annotation_text": {
                    "type": "string",
                    "description": "Text of the annotation.",
                },
                "processed_note_text": {
                    "type": "string",
                    "description": "Processed note text. Reword the note to be more concise and clear. Do not get creative, if it is already concise and clear and perfect you can leave this one out.",
                }
            },
            "required": ["category_name", "annotation_text"],
        }
    }
