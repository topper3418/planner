import sqlite3
import logging
from typing import Optional
from pydantic import BaseModel, Field, PrivateAttr

from src.config import NOTES_DATABASE_FILEPATH
from .note import Note


logger = logging.getLogger(__name__)


def get_connection(connection_path: str = NOTES_DATABASE_FILEPATH):
    """
    Establishes a connection to the SQLite database.
    """
    connection = sqlite3.connect(connection_path)
    return connection


class Todo(BaseModel):
    """
    represents something the user wants to do
    """
    id: int = Field(..., description="Unique identifier for the todo")
    target_start_time: Optional[str] = Field(None, description="Target start time of the todo")
    target_end_time: Optional[str] = Field(None, description="Target end time of the todo")
    todo_text: str = Field(..., description="Text of the todo")
    source_note_id: int = Field(..., description="ID of the source note")

    _source_note: Optional[Note] = PrivateAttr(default=None)
    @property
    def source_note(self) -> Note:
        """
        Returns the note associated with the todo.
        """
        if self._source_note is None:
            self._source_note = Note.get_by_id(self.source_note_id)
            if self._source_note is None:
                logger.error(f"Note with ID {self.source_note_id} not found in the database.")
                raise ValueError(f"Note with ID {self.source_note_id} not found in the database.")
        return self._source_note
    @source_note.setter
    def source_note(self, note: Note):
        if not note.id == self.source_note_id:
            raise ValueError("note ID does not match source_note_id")
        self._source_note = note

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the todos table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_start_time DATETIME DEFAULT NULL,
                target_end_time DATETIME DEFAULT NULL,
                todo_text TEXT NOT NULL,
                source_note_id INTEGER NOT NULL
            );
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
    
    @classmethod
    def from_sqlite_row(cls, row) -> "Todo":
        """
        Creates a Todo instance from a SQLite row.
        """
        return cls(
            id=row[0],
            target_start_time=row[1],
            target_end_time=row[2],
            todo_text=row[3],
            source_note_id=row[4]
        )

    @classmethod
    def get_by_id(cls, todo_id: int) -> "Todo":
        """
        Retrieves a Todo instance by its ID.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_sqlite_row(row)
            else:
                logger.error(f"Todo with ID {todo_id} not found in the database.")
                raise ValueError(f"Todo with ID {todo_id} not found in the database.")

    def refresh(self) -> "Todo":
        """
        Refreshes the Todo instance by reloading it from the database.
        """
        copy = self.get_by_id(self.id)
        self.target_start_time = copy.target_start_time
        self.target_end_time = copy.target_end_time
        self.todo_text = copy.todo_text
        return self

    def save(self):
        """
        Saves the Todo instance to the database.
        """
        query = '''
            UPDATE todos
            SET target_start_time = ?, target_end_time = ?, todo_text = ?
            WHERE id = ?;
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.target_start_time, self.target_end_time, self.todo_text, self.id))
            conn.commit()

    @classmethod
    def create(cls, todo_text, source_note_id, target_start_time: Optional[str]=None, target_end_time: Optional[str]=None) -> "Todo":
        """
        Creates a new Todo instance and saves it to the database.
        """
        query = '''
            INSERT INTO todos (target_start_time, target_end_time, todo_text, source_note_id)
            VALUES (?, ?, ?, ?);
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (target_start_time, target_end_time, todo_text, source_note_id))
            conn.commit()
            return cls(
                id=0, # ID will be auto-incremented
                target_start_time=target_start_time,
                target_end_time=target_end_time,
                todo_text=todo_text,
                source_note_id=source_note_id
            )




