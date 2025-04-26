import os

from src import db
from src.processor_v2 import NoteProcessor

# make sure its using openai 
os.environ["PLANNER_CHAT_SERVICE"] = "openai"

# get the last note
note = db.Note.get_all(limit=1)[0]
# create a note processor
processor = NoteProcessor(note)

# process the note
processor.process_annotation()
