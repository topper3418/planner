from datetime import datetime
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


class Action(BaseModel):
    """
    Represents an action that the user took
    """
    id: int = Field(..., description="Unique identifier for the action")
    start_time: str = Field(..., description="Start time of the action")
    end_time: Optional[str] = Field(None, description="End time of the action")
    action_text: str = Field(..., description="Text of the action")
    source_note_id: int = Field(..., description="ID of the source note")

    _source_note: Optional[Note] = PrivateAttr(default=None)
    @property
    def source_note(self) -> Note:
        """
        Returns the note associated with the action.
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
        Returns the SQL query to create the actions table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME DEFAULT NULL,
                action_text TEXT NOT NULL,
                source_note_id INTEGER NOT NULL
            )
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def from_sqlite_row(cls, row):
        """
        Converts a SQLite row to a DbAction instance.
        """
        return cls(
            id=row[0],
            start_time=row[1],
            end_time=row[2],
            action_text=row[3],
            source_note_id=row[4],
        )

    @classmethod
    def get_by_id(cls, action_id: int):
        """
        Retrieves an action by its ID.
        """
        query = 'SELECT * FROM actions WHERE id = ?'
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (action_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_sqlite_row(row)
            else:
                return None

    def refresh(self):
        copy = self.get_by_id(self.id)
        if copy:
            self.start_time = copy.start_time
            self.end_time = copy.end_time
            self.action_text = copy.action_text
        else:
            logger.error(f"Action with ID {self.id} not found in the database.")

    def save(self):
        """
        Saves the action to the database.
        """
        query = '''
            UPDATE actions
            SET start_time = ?, end_time = ?, action_text = ?
            WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.start_time, self.end_time, self.action_text, self.id))
            conn.commit()

    @classmethod
    def create(cls, action_text: str, start_time: str, source_note_id: int, end_time: Optional[str] = None):
        """
        Creates a new action in the database.
        """
        query = '''
            INSERT INTO actions (start_time, end_time, action_text, source_note_id)
            VALUES (?, ?, ?, ?)
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (start_time, end_time, action_text, source_note_id))
            conn.commit()
            action_id = cursor.lastrowid
        if action_id is None:
            raise ValueError("Failed to create action in the database.")
        action = cls.get_by_id(action_id)
        return action
