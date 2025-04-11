import logging
import src.db as db

from .client import GrokChatClient

logger = logging.getLogger(__name__)


def create_command(annotation: db.Annotation) -> db.Command | None:
    """
    Create a command from an annotation.
    """
    if annotation.category.name != "command":
        raise ValueError(f"annotation category is not command: {annotation.category.name}")
    client = GrokChatClient()
    client.load_system_message("create_command")
    logger.debug(f"system message is:\n{client.system_message}")

    response = client.chat(annotation.annotation_text)
    logger.info(f"response is:\n{response}")

    # parse the response
    command_text = response.get('command_text')
    if not command_text:
        raise ValueError(f"Command text not found in response: {response}")
    value_before = response.get('value_before')
    if not value_before:
        raise ValueError(f"Value before not found in response: {response}")
    desired_value = response.get('desired_value')
    if not desired_value:
        raise ValueError(f"Desired value not found in response: {response}")

    try:
        command = db.Command.create(
            command_text=command_text,
            value_before=value_before,
            desired_value=desired_value,
            source_annotation_id=annotation.id,
        )
    except TypeError as e:
        raise ValueError(f"Invalid response format: {e}")
    logger.info("command created:\n" + str(command))
    if command:
        command.source_annotation = annotation
    return command

