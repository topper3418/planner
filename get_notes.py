import sqlite3
from src import db, pretty_printing

import time


def main():
   # Get all notes
   notes = db.Note.read(limit=75)
   notes.reverse()
   pretty_notes = pretty_printing.strf_notes(notes, show_processed_text=True)
   # clear the console
   print("\033[H\033[J")
   print("===================================")
   print("Notes:                            ||")
   print("===================================")
   print(pretty_notes)


if __name__ == "__main__":
   while True:
      try:
         main()
         time.sleep(.5)
      except sqlite3.OperationalError as e:
         print("Database is locked. Retrying in 1 second...")
         time.sleep(1)
      
