import logging
from pprint import pformat

from .. import db
from .client import GrokChatClient

logger = logging.getLogger(__name__)


def get_command_text(annotation: db.Annotation) -> str:
    """
    Get the command text from the annotation.
    """
    if annotation.category.name != "command":
        raise ValueError(f"annotation category is not command: {annotation.category.name}")
    client = GrokChatClient()
    client.load_system_message("get_command_text")
    response = client.chat(annotation.note.processed_note_text)
    logger.info(f"get command text response is:\n{response}")
    command_text = response.get('command_text')
    if not command_text:
        raise ValueError(f"Command text not found in response: {response}")
    return command_text


def get_target_note_id(annotation: db.Annotation) -> int:
    client = GrokChatClient()
    client.load_system_message("get_target_id", command=annotation.model_dump())
    target_note_id = 0
    ii = 0
    inc = 5
    while int(target_note_id) == 0:
        # only allow searching backwards 150 notes
        if ii * inc > 150:
            return 0
        # in case this is going back and being processed, need to make sure a
        # command doesn't target a note in the future, that the user wasn't 
        # meaning to target
        notes = db.Note.get_all(offset=ii*inc, limit=inc, before=annotation.note.timestamp)
        if not notes:
            break
        notes_str = "\n".join([note.model_dump_json() for note in notes])
        logger.debug('notes found:\n' + notes_str)
        response = client.chat(notes_str)
        logger.info(f"get command context response is:\n{response}")
        target_note_id = response.get('target_id')
        if target_note_id is None:
            raise ValueError(f"Target note ID not found in response: {response}")
        if not int(target_note_id):
            ii += 1
            logger.info(f"no tarmet note found, trying again with offset {ii}")
    return int(target_note_id)


def get_target_todo_id(annotation: db.Annotation) -> int:
    client = GrokChatClient()
    client.load_system_message("get_target_id", command=annotation.model_dump())
    target_todo_id = 0
    ii = 0
    inc = 5
    while int(target_todo_id) == 0:
        # only allow searching backwards 150 notes
        if ii * inc > 150:
            return 0
        # in case this is going back and being processed, need to make sure a
        # command doesn't target a note in the future, that the user wasn't 
        # meaning to target
        todos = db.Todo.read(offset=ii*inc, limit=inc)
        if not todos:
            break
        todos_str = "\n".join([todo.model_dump_json() for todo in todos])
        logger.info('todos found:\n' + todos_str)
        response = client.chat(todos_str)
        logger.info(f"get command context response is:\n{response}")
        target_todo_id = response.get('target_id')
        if target_todo_id is None:
            raise ValueError(f"Target todo ID not found in response: {response}")
        if not int(target_todo_id):
            ii += 1
            logger.info(f"no tarmet todo found, trying again with offset {ii}")
    return int(target_todo_id)


def get_target_action_id(annotation: db.Annotation) -> int:
    client = GrokChatClient()
    annotation.note  # ensure the note is loaded
    client.load_system_message("get_target_id", command=annotation.model_dump())
    target_action_id = 0
    ii = 0
    inc = 5
    while int(target_action_id) == 0:
        # only allow searching backwards 150 notes
        if ii * inc > 150:
            return 0
        # in case this is going back and being processed, need to make sure a
        # command doesn't target a note in the future, that the user wasn't 
        # meaning to target
        actions = db.Action.read(offset=ii*inc, limit=inc)
        if not actions:
            break
        actions_str = "\n".join([action.model_dump_json() for action in actions])
        logger.info('actions found:\n' + actions_str)
        response = client.chat(actions_str)
        logger.info(f"get command context response is:\n{response}")
        target_action_id = response.get('target_id')
        if target_action_id is None:
            raise ValueError(f"Target action ID not found in response: {response}")
        if not int(target_action_id):
            ii += 1
            logger.info(f"no tarmet action found, trying again with offset {ii}")
    return int(target_action_id)


def create_command(annotation: db.Annotation) -> db.Command | None:
    """
    Create a command from an annotation.
    """
    if annotation.category.name != "command":
        raise ValueError(f"annotation category is not command: {annotation.category.name}")
    command_text = get_command_text(annotation)
    if "note" in command_text:
        target_id = get_target_note_id(annotation)
        target = db.Note.get_by_id(target_id) if target_id else None
        if not target:
            annotation.note.processing_error = "no target note found"
            annotation.note.save()
            return None
        # get the note as a string
        target_dict = target.model_dump()
        if "category" in command_text:
            note_annotation = db.Annotation.get_by_note_id(target_id)
            if not note_annotation:
                annotation.note.processing_error = "no target note found"
                annotation.note.save()
                return None
            target_dict["category"] = note_annotation.category.name
            target_dict["available_categories"] = [category.name for category in db.Category.get_all()]
        target_str = pformat(target_dict)
    elif "todo" in command_text:
        target_id = get_target_todo_id(annotation)
        target = db.Todo.get_by_id(target_id) if target_id else None
        if not target:
            annotation.note.processing_error = "no target todo found"
            annotation.note.save()
            return None
        target_str = target.model_dump_json()
    elif "action" in command_text:
        target_id = get_target_action_id(annotation)
        target = db.Action.get_by_id(target_id) if target_id else None
        if not target:
            annotation.note.processing_error = "no target action found"
            return None
        target_str = target.model_dump_json()
    else:  # handle failure case for "get_command"
        logger.error(f"no command found matching user input: {command_text}")
        note = annotation.note
        note.processing_error = "no command found matching user input"
        note.save()
        logger.warning('note:' + str(note))
        note_fetched = db.Note.get_by_id(note.id)
        logger.warning('note fetched:' + str(note_fetched))
        return None
    if target_id == 0:  # handle failure case for "get_target_id"
        logger.error(f"no target found for command: {command_text}")
        note = annotation.note
        note.processing_error = "no target found"
        note.save()
        return None
    client = GrokChatClient()
    client.load_system_message("create_command", command_text=command_text, annotation=annotation.model_dump())

    response = client.chat(target_str)
    logger.info(f"response is:\n{response}")

    # parse the response
    value_before = response.get('value_before')
    desired_value = response.get('desired_value')

    if command_text == "no_match_found":
        annotation.note.processing_error = "no_match_found"
        annotation.note.save()

    try:
        command = db.Command.create(
            command_text=command_text,
            value_before=value_before or "",
            desired_value=desired_value or "",
            source_annotation_id=annotation.id,
            target_id=target_id,
        )
    except TypeError as e:
        raise ValueError(f"Invalid response format: {e}")
    logger.info("command created:\n" + str(command))
    if command:
        command.source_annotation = annotation
    command.save()
    return command

