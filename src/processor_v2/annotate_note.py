import logging

from openai.types.chat import ChatCompletionToolParam

from ..config import TIMESTAMP_FORMAT
from ..db import Note, Category, Annotation

logger = logging.getLogger(__name__)


def annotate_note(note: Note, category_name: str, annotation_text) -> Annotation:
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

    return annotation

categories = Category.get_all()

def render_category_str(category: Category) -> str:
    """
    Render a category as a string.
    """
    return f"\t - {category.name} - {category.description}"

annotate_note_tool: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "annotate_note",
        "description": f"""Annotate a note with a category and give a third person description of the note.
         - refer to the user as "the user"
         - choose the relevant category from the following list:
         {'\n'.join(render_category_str(category) for category in categories)}
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
            },
            "required": ["category_name", "annotation_text"],
        }
    }
}
