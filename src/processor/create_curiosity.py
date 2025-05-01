import logging

from openai.types.responses import FunctionToolParam, ToolParam



from ..db import Note, Curiosity


logger = logging.getLogger(__name__)


def create_curiosity(
    note: Note,
    curiosity_text: str,
) -> Curiosity:
    """
    Create a curiosity, when the user logs a curiosity.
    """

    # Create the curiosity
    curiosity = Curiosity.create(
        curiosity_text=curiosity_text,
        source_note_id=note.id,
    )
    curiosity.save()

    return curiosity


def get_create_curiosity_tool() -> ToolParam:
    return FunctionToolParam(
        type="function",
        name="create_curiosity",
        description="Create a curiosity, when the user logs a curiosity.",
        parameters={
            "type": "object",
            "properties": {
                "curiosity_text": {
                    "type": "string",
                    "description": "do your best to bring the user the information they are looking for in a medium length paragraph. If their question can be answered in just a few words, the more concise and to the point the better. If you are unable to give the information in the space alotted, please instead use the space to provide them with instructions or a general strategy on how to find the information they are looking for.",
                },
            },
            "required": ["curiosity_text"],
            "additionalProperties": False,
        },
        strict=True,
    )
