import logging
from pprint import pformat

from src import db, processor

logger = logging.getLogger(__name__)
text_file_logger = logging.getLogger("text_file_logger")
text_file_logger.setLevel(logging.INFO)
text_file_handler = logging.FileHandler("engine.log")
text_file_handler.setLevel(logging.INFO)
text_file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
text_file_handler.setFormatter(text_file_formatter)
text_file_logger.addHandler(text_file_handler)


def cycle_note_processor():
    """
    This function will cycle through notes one at a time in the database and process them.
    """
    note = db.Note.get_next_unprocessed_note()
    if not note:
        logger.debug("No unprocessed notes found.")
        return
    note_processor = processor.NoteProcessor(note)
    note_processor.process()

    processing_payload = pformat(note_processor.to_json())
    text_file_logger.info(f"Note processing payload:\n{processing_payload}")
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
