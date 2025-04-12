import logging
import src.db as db

from .client import GrokChatClient

logger = logging.getLogger(__name__)


def note_to_str(note: db.Note) -> str:
    annotation = db.Annotation.get_by_note_id(note.id)
    return f"ID:{note.id} - {'uncategorized' if not annotation else annotation.category.name} - {note.timestamp}: {note.note_text}"


def get_target_id(annotation_id) -> int:
    client = GrokChatClient()
    annotation = db.Annotation.get_by_id(annotation_id)
    annotation.note  # load the note
    client.load_system_message("get_target_id", command=annotation.model_dump())
    logger.debug(f"system message is:\n{client.system_message}")
    target_note_id = 0
    ii = 0
    inc = 5
    while int(target_note_id) == 0:
        # only allow searching backwards 150 notes
        if ii * inc > 150:
            return 0
        notes = db.Note.read(offset=ii*inc, limit=inc)
        if not notes:
            break
        notes_str = "\n".join([note_to_str(note) for note in notes])
        logger.info('notes found:\n' + notes_str)
        response = client.chat(notes_str)
        logger.info(f"get command context response is:\n{response}")
        target_note_id = response.get('target_note_id')
        if target_note_id is None:
            raise ValueError(f"Target note ID not found in response: {response}")
        if not int(target_note_id):
            ii += 1
            logger.info(f"no target note found, trying again with offset {ii}")
    return int(target_note_id)


def create_command(annotation: db.Annotation) -> db.Command | None:
    """
    Create a command from an annotation.
    """
    if annotation.category.name != "command":
        raise ValueError(f"annotation category is not command: {annotation.category.name}")
    target_id = get_target_id(annotation.id)
    if target_id == 0:
        annotation.note.processing_error = "no target note found"
        return None
    target_note = db.Note.get_by_id(target_id)
    if not target_note:
        raise ValueError(f"Target note with ID {target_id} not found")
    client = GrokChatClient()
    client.load_system_message("create_command", context=note_to_str(target_note))
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

    if command_text == "no_match_found":
        annotation.note.processing_error = "no_match_found"
        return None

    try:
        command = db.Command.create(
            command_text=command_text,
            value_before=value_before,
            desired_value=desired_value,
            source_annotation_id=annotation.id,
            target_id=target_id,
        )
    except TypeError as e:
        raise ValueError(f"Invalid response format: {e}")
    logger.info("command created:\n" + str(command))
    if command:
        command.source_annotation = annotation
    return command

