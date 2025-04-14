import sqlite3
from src import db, pretty_printing

import time


def main():
   # Get all todos
   todos = db.Todo.read()
   title = pretty_printing.banner("Todos")
   todos_strings = pretty_printing.strf_todos(todos)
   # clear the console
   print("\033[H\033[J")
   # print the title
   print(title)
   print(todos_strings)


if __name__ == "__main__":
   while True:
      try:
         main()
         time.sleep(.5)  
      except sqlite3.OperationalError as e:
         print("Database is locked. Retrying in 1 second...")
         time.sleep(1)
