from pprint import pformat

from src import db, processor, logging

logger = logging.get_logger(__name__)


def cycle_note_processor():
    """
    This function will cycle through notes one at a time in the database and process them.
    """
    note = db.Note.get_next_unprocessed_note()
    if not note:
        logger.debug("No unprocessed notes found.")
        return
    note_processor = processor.NoteProcessor(note)
    note_processor.process_note()

    # processing_payload = pformat(note_processor.to_json())
    # text_file_logger.info(f"Note processing payload:\n{processing_payload}")
    return note


def cycle():
    """
    Main function to run the note processor and annotation reprocessor.
    """
    note = cycle_note_processor()
    if not note:
        return
    return {
        "note": note,
    }
