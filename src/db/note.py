import sqlite3
import logging
from pydantic import BaseModel, Field

from src.config import NOTES_DATABASE_FILEPATH


logger = logging.getLogger(__name__)


def get_connection(connection_path: str = NOTES_DATABASE_FILEPATH):
    """
    Establishes a connection to the SQLite database.
    """
    connection = sqlite3.connect(connection_path)
    return connection


class Note(BaseModel):
    """
    Represents a note with a timestamp and text.
    """
    id: int = Field(..., description="Unique identifier for the note")
    timestamp: str = Field(..., description="Timestamp of the note")
    note_text: str = Field(..., description="Text of the note")
    processed_note_text: str = Field("", description="The text of the note, as processed by the LLM")

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the notes table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                note_text TEXT NOT NULL,
                processed_note_text TEXT DEFAULT 0
            )
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def from_sqlite_row(cls, row):
        """
        Converts a SQLite row to a DbNote instance.
        """
        return cls(
            id=row[0],
            timestamp=row[1],
            note_text=row[2],
            processed_note_text=row[3]
        )

    @classmethod    
    def get_next_unprocessed_note(cls):
        """
        Returns the SQL query to fetch the next unprocessed note.
        """
        query = '''
            SELECT * FROM notes WHERE processed_note_text = ""
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            unprocessed_note = cursor.fetchone()
            if unprocessed_note:
                return cls.from_sqlite_row(unprocessed_note)
            else:
                return None

    def refresh(self):
        copy = self.get_by_id(self.id)
        if copy is None:
            raise Exception("Failed to refresh note.")
        self.timestamp = copy.timestamp
        self.note_text = copy.note_text
        self.processed_note_text = copy.processed_note_text
        return self

    @classmethod
    def get_by_id(cls, note_id):
        """
        Fetches a note by its ID.
        """
        query = '''
            SELECT * FROM notes WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (note_id,))
            note = cursor.fetchone()
            if note:
                return cls.from_sqlite_row(note)
            else:
                return None

    @classmethod
    def create(cls, note_text, timestamp=None, processed_note_text=None):
        """
        Inserts a new note into the database.
        """
        query = '''
            INSERT INTO notes (note_text) VALUES (?)
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (note_text,))
            conn.commit()
            if cursor.lastrowid is None:
                raise Exception("Failed to create note.")
            note = cls.get_by_id(cursor.lastrowid)
            if note is None:
                raise Exception("Failed to retrieve created note.")
            # less common, likely only in tests
            if timestamp or processed_note_text:
                if timestamp:
                    note.timestamp = timestamp
                if processed_note_text:
                    note.processed_note_text = processed_note_text
                note.save()
            return note

    def save(self):
        """
        Updates the note in the database.
        """
        query = '''
            UPDATE notes SET timestamp = ?, note_text = ?, processed_note_text = ? WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.timestamp, self.note_text, self.processed_note_text, self.id))
            conn.commit()


    @classmethod
    def read(cls, before=None, after=None, search=None, limit=15):
        """
        Fetches notes from the database with optional filters.
        """
        query = """SELECT id, timestamp, note_text, processed_note_text FROM notes WHERE 1=1"""
        params = []

        if before:
            query += ' AND timestamp < ?'
            params.append(before)
        if after:
            query += ' AND timestamp > ?'
            params.append(after)
        if search:
            query += ' AND note_text LIKE ?'
            params.append(f'%{search}%')
        
        query += ' ORDER BY timestamp LIMIT ?'
        params.append(limit)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            notes = cursor.fetchall()
            return [cls.from_sqlite_row(note) for note in notes]
