from src import db

import time


def note_to_str(note: db.Note) -> str:
   """
   Convert a note to a string representation.
   """
   annotation = db.Annotation.get_by_note_id(note.id)
   if annotation is None:
      category_name = "uncategorized"
   else:
      category_name = annotation.category.name
   return f"{note.id} [{category_name}]: {note.timestamp} - {note.note_text}"

def main():
   # Get all notes
   notes = db.Note.read(limit=75)
   # Print the notes
   string_notes = [note_to_str(note) for note in notes]
   string_notes.reverse()
   # clear the console
   print("\033[H\033[J")
   print("===================================")
   print("Notes:                            ||")
   print("===================================")
   for note in string_notes:
      print(note)


if __name__ == "__main__":
   while True:
      main()
      time.sleep(.5)
      
