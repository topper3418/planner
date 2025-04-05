import sqlite3
from pydantic import BaseModel, Field

from src.config import NOTES_DATABASE_FILEPATH


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
    processed: bool = Field(False, description="Whether the note has been processed")

    def mark_as_processed(self):
        """
        Marks the note as processed in the database.
        """
        query = '''
            UPDATE notes SET processed = 1 WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.id,))
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
            processed=row[3] == 1
        )

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
                processed BOOLEAN DEFAULT 0
            )
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod    
    def get_next_unprocessed_note(cls):
        """
        Returns the SQL query to fetch the next unprocessed note.
        """
        query = '''
            SELECT * FROM notes WHERE processed = 0
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            unprocessed_note = cursor.fetchone()
            if unprocessed_note:
                return cls.from_sqlite_row(unprocessed_note)
            else:
                return None

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
    def create(cls, note_text):
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
            return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def read(cls, before=None, after=None, search=None, limit=15):
        """
        Fetches notes from the database with optional filters.
        """
        query = """SELECT id, timestamp, note_text, processed FROM notes WHERE 1=1"""
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
