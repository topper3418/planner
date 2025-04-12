from src import db

import time

def todo_to_str(todo: db.Todo) -> str:
   """
    Convert a todo to a string.
    """
   return f"[{"X" if todo.complete else " "}]{todo.id}: {todo.todo_text} - {todo.target_start_time} - {todo.target_end_time}"

def main():
   # Get all todos
   todos = db.Todo.read()
   todos_strings = [todo_to_str(todo) for todo in todos]
   # clear the console
   print("\033[H\033[J")
   print("===================================")
   print("Todos:                            ||")
   print("===================================")
   # Print the todos
   for todo in todos_strings:
      print(todo)

if __name__ == "__main__":
   while True:
      main()
      time.sleep(.5)  
