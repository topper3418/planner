import logging
import src.db as db

from .client import GrokChatClient

logger = logging.getLogger(__name__)


def get_command_context(command_text) -> str:
    client = GrokChatClient()
    client.load_system_message("get_command_note_search")
    logger.debug(f"system message is:\n{client.system_message}")
    response = client.chat(command_text)
    notes = db.Note.read(
        before=response.get('start_time'), 
        after=response.get('end_time'), 
        search=response.get('search_text')
    )
    if not notes:
        # try again without the search just in case
        logger.warning("No notes found with the given search criteria. Trying again without search.")
        notes = db.Note.read(
            before=response.get('start_time'), 
            after=response.get('end_time')
        )
    if not notes:
        # hopefully this is because the user was so vague that it was a new note. 
        logger.warning("No notes found with the given time criteria. Trying again without time.")
        notes = db.Note.read()
    def note_to_str(note: db.Note) -> str:
        annotation = db.Annotation.get_by_note_id(note.id)
        return f"ID:{note.id} - {'uncategorized' if not annotation else annotation.category.name} - {note.timestamp}: {note.note_text}"
    notes_str = "\n".join([note_to_str(note) for note in notes])
    return notes_str


def create_command(annotation: db.Annotation) -> db.Command | None:
    """
    Create a command from an annotation.
    """
    if annotation.category.name != "command":
        raise ValueError(f"annotation category is not command: {annotation.category.name}")
    command_context = get_command_context(annotation.annotation_text)
    client = GrokChatClient()
    client.load_system_message("create_command", context=command_context)
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
    target_id = response.get('target_id')
    if not target_id:
        raise ValueError(f"Target ID not found in response: {response}")

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

