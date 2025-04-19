import logging
import src.db as db

from ..grok import GrokChatClient

logger = logging.getLogger(__name__)


def todo_to_str(todo: db.Todo) -> str:
    return f"ID:{todo.id} created: {todo.source_annotation.note.timestamp} - target_start: {todo.target_start_time} - target_end: {todo.target_end_time}: {todo.todo_text}"


def apply_action_to_todo(action: db.Action):
    client = GrokChatClient()
    action.source_annotation.note  # load the note and annotation
    client.load_system_message("apply_action_to_todo", action=action.model_dump())
    target_todo_id = 0
    ii = 0
    inc = 5
    while int(target_todo_id) == 0:
        todos = db.Todo.get_incomplete(offset=ii*inc, limit=inc)
        if not todos:
            break
        todos_str = "\n".join([todo_to_str(todo) for todo in todos])
        logger.info('todos found:\n' + todos_str)
        response = client.chat(todos_str)
        logger.info(f"apply action to todo response is:\n{response}")
        target_todo_id = response.get('target_todo_id')
        if target_todo_id is None:
            raise ValueError(f"Target todo ID not found in response: {response}")
        if not int(target_todo_id):
            ii += 1
            logger.info(f"no target todo found, trying again with offset {ii}")
    return int(target_todo_id)


def create_action(annotation: db.Annotation):
    """
    Create an action from an annotation.
    """
    if annotation.category.name != "action":
        raise ValueError(f"annotation category is not action: {annotation.category.name}")
    client = GrokChatClient()
    client.load_system_message("create_action")
    
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
            source_annotation_id=annotation.id,
        )
    except TypeError as e:
        raise ValueError(f"Invalid response format: {e}")
    logger.info("action created:\n" + str(action))
    if action:
        action.source_annotation = annotation
        # see if the action is relevant to any of our incomplete todos
        target_todo_id = apply_action_to_todo(action)
        if target_todo_id:
            action.todo_id = target_todo_id
            action.save()
            todo = db.Todo.get_by_id(target_todo_id)
            todo.complete = True
            todo.save()
            logger.info(f"todo found for action {action.id}:\n" + str(todo))
        else:
            logger.info(f"no todo found for action {action.id}")

    return action


