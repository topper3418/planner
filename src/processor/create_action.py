import logging
import src.db as db

from .client import GrokChatClient

logger = logging.getLogger(__name__)


def create_action(annotation: db.Annotation):
    """
    Create an action from an annotation.
    """
    if not annotation:
        raise ValueError("annotation is None")
    if annotation.category.name != "action":
        raise ValueError(f"annotation category is not action: {annotation.category.name}")
    client = GrokChatClient()
    client.load_system_message("create_action")
    logger.debug(f"system message is:\n{client.system_message}")
    
    response = client.chat(annotation.annotation_text)
    logger.info(f"response is:\n{response}")

    # parse the response
    action_text = response.get('action_text')
    if not action_text:
        raise ValueError(f"Action text not found in response: {response}")
    start_time = response.get('start_time')
    if not start_time:
        raise ValueError(f"Start time not found in response: {response}")
    try:
        action = db.Action.create(
            action_text=action_text,
            start_time=start_time,
            end_time=response.get('end_time'),
            source_note_id=annotation.note_id,
        )
    except TypeError as e:
        raise ValueError(f"Invalid response format: {e}")
    logger.info("action created:\n" + str(action))
    if action:
        action.source_note = annotation.note
    return action


