import logging
import json

from .client import GrokChatClient
from .. import db

logger = logging.getLogger(__name__)


sys_message_map = {
    "action": "annotate_action",
    "todo": "annotate_todo",
    "curiosity": "annotate_curiosity",
    "observation": "annotate_observation",
    "command": "annotate_command",
}


def annotate_note(note: db.Note, category: db.Category) -> db.Annotation:
    """
    Annotate a note using the GrokChatClient.
    """
    # Initialize the chat client
    client = GrokChatClient()

    # Load the system message
    client.load_system_message(sys_message_map[category.name])
    logger.debug(f"system message is:\n{client.system_message}")
    
    # Send the note text to the chat client for annotation
    response = client.chat(note.note_text, role="user")
    
    # Parse the response to get the annotation text
    processed_note_text = response.get(category.name)
    if not processed_note_text:
        raise ValueError(f"Annotation text not found in response: {response}")
    logger.info(f"note {note.note_text} processed to: {processed_note_text}")
    note.processed_note_text = processed_note_text
    annotation_text = response.get('response')
    if not annotation_text:
        raise ValueError(f"Annotation text not found in response: {response}")
    logger.info(f"note {note.note_text} annotated with: {annotation_text}")
    
    # Create an annotation in the database
    annotation = db.Annotation.create(
        note_id=note.id,
        category_id=category.id,
        annotation_text=annotation_text,
    )

    return annotation
