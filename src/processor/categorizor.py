import logging
import json

from .client import GrokChatClient
from .. import db

logger = logging.getLogger(__name__)

def categorize_note(note: db.Note) -> db.Category:
    """
    Categorize a note using the GrokChatClient.
    """
    # Initialize the chat client
    client = GrokChatClient()

    categories = db.Category.get_all()

    # Load the system message
    client.load_system_message(
        "give_topic",
        categories=str([category.model_dump_json() for category in categories]),
    )
    
    # Send the note text to the chat client for categorization
    response = client.chat(note.model_dump_json(), role="user")
    
    # Parse the response to get the category name
    category_name = response.get('category')
    logger.info(f"note {note.note_text} categorized as {category_name}")
    
    # Find the category in the database
    category = db.Category.find_by_name(category_name)
    
    if not category:
        raise ValueError(f"Category '{category_name}' not found in database.")

    return category
