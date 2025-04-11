import logging
import src.db as db

from .client import GrokChatClient

logger = logging.getLogger(__name__)


def create_todo(annotation: db.Annotation):
    """
    Create a todo from an annotation.
    """
    if annotation.category.name != "todo":
        raise ValueError(f"annotation category is not todo: {annotation.category.name}")
    client = GrokChatClient()
    client.load_system_message("create_todo")
    logger.debug(f"system message is:\n{client.system_message}")

    response = client.chat(annotation.annotation_text)
    logger.info(f"response is:\n{response}")

    # parse the response
    todo_text = response.get('todo_text')
    if not todo_text:
        raise ValueError(f"Todo text not found in response: {response}")
    try:
        todo = db.Todo.create(
            todo_text=todo_text,
            target_start_time=response.get('target_start_time'),
            target_end_time=response.get('target_end_time'),
            source_annotation_id=annotation.id,
        )
    except TypeError as e:
        raise ValueError(f"Invalid response format: {e}")
    logger.info("todo created:\n" + str(todo))
    if todo:
        todo.source_annotation = annotation
    return todo


