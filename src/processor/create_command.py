import logging
import src.db as db

from .client import GrokChatClient

logger = logging.getLogger(__name__)


def create_command(annotation: db.Annotation):
    """
    Create a command from an annotation.
    """
    if annotation.category.name != "command":
        raise ValueError(f"annotation category is not command: {annotation.category.name}")
    client = GrokChatClient()
    client.load_system_message("create_command")
    logger.debug(f"system message is:\n{client.system_message}")

    response = client.chat(annotation.annotation_text)

    # parse the response
    command_text = response.get('command_text')
    if not command_text:
        raise ValueError(f"Command text not found in response: {response}")
    # in addition to text, a command might have a 
    #  - value before
    #  - desired value
    #  - source annotation

