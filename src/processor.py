from . import db


def process_unprocessed_note():
    note = db.Note.get_next_unprocessed_note()
    if note:
        # Here you would process the note (e.g., send it to OpenAI)
        # For demonstration, we'll just print it
        print(f"Processing note: {note.note_text}")
        
        # After processing, mark the note as processed
        note.mark_as_processed()
    else:
        print("No unprocessed notes found.")


# this is where I put the grok integration. 
# put your xai key in your own environment
# come up with a couple more tables to store shit in
# then go
