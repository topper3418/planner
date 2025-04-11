import logging

from .. import db
from .categorizor import categorize_note
from .annotator import annotate_note

logger = logging.getLogger(__name__) 





def process_unprocessed_note():
    note = db.Note.get_next_unprocessed_note()
    if note:
        # Here you would process the note (e.g., send it to OpenAI)
        # For demonstration, we'll just print it
        logger.info(f"Processing note: {note.note_text}")
        
        # After processing, mark the note as processed
        note.mark_as_processed()
        return note
    else:
        print("No unprocessed notes found.")


# this is where I put the grok integration. 
# put your xai key in your own environment
# come up with a couple more tables to store shit in
# then go
