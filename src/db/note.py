import sqlite3
import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from ..config import TIMESTAMP_FORMAT
from .connection import get_connection


logger = logging.getLogger(__name__)


class Note(BaseModel):
    """
    Represents a note with a timestamp and text.
    """
    id: int = Field(..., description="Unique identifier for the note")
    timestamp: datetime = Field(..., description="Timestamp of the note")
    note_text: str = Field(..., description="Text of the note")
    processed_note_text: str = Field("", description="The text of the note, as processed by the LLM")
    processing_error: str = Field("", description="Error message if processing failed")

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the notes table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
                note_text TEXT NOT NULL,
                processed_note_text TEXT DEFAULT "",
                processing_error TEXT DEFAULT ""
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
            timestamp=datetime.strptime(row[1], TIMESTAMP_FORMAT),
            note_text=row[2],
            processed_note_text=row[3],
            processing_error=row[4],
        )

    def reload(self):
        """
        Reloads the note from the database.
        """
        copy = self.get_by_id(self.id)
        if copy is None:
            raise Exception("Failed to reload note.")
        self.timestamp = copy.timestamp
        self.note_text = copy.note_text
        self.processed_note_text = copy.processed_note_text
        return self

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
    def create(cls, note_text, timestamp: Optional[datetime | str]=None, processed_note_text=None):
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
                    if isinstance(timestamp, str):
                        timestamp = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
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
            cursor.execute(query, (datetime.strftime(self.timestamp, TIMESTAMP_FORMAT), self.note_text, self.processed_note_text, self.id,))
            conn.commit()

    @classmethod
    def get_all(cls, before=None, after=None, search=None, offset=0, limit=15):
        """
        Fetches notes from the database with optional filters.
        """
        query = """SELECT id, timestamp, note_text, processed_note_text, processing_error FROM notes WHERE 1=1"""
        params = []

        if before:
            query += ' AND timestamp < ?'
            if isinstance(before, datetime):
                before = datetime.strftime(before, TIMESTAMP_FORMAT)
            params.append(before)
        if after:
            query += ' AND timestamp > ?'
            if isinstance(after, datetime):
                after = datetime.strftime(after, TIMESTAMP_FORMAT)
            params.append(after)
        if search:
            query += ' AND note_text LIKE ?'
            params.append(f'%{search}%')
        
        query += ' ORDER BY id desc LIMIT ? OFFSET ?'
        params.append(limit)
        params.append(offset)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            notes = cursor.fetchall()
            return [cls.from_sqlite_row(note) for note in notes]

    @classmethod
    def export_csv(cls, filepath: str, stripped: bool=True):
        """
        Exports all notes to a CSV file.
        """
        import csv
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM notes')
            rows = cursor.fetchall()
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if stripped: 
                    writer.writerow(['timestamp', 'note_text'])
                else:
                    writer.writerow(['id', 'timestamp', 'note_text', 'processed_note_text', 'processing_error'])
                for row in rows:
                    if stripped:
                        writer.writerow([datetime.strptime(row[1], TIMESTAMP_FORMAT).strftime(TIMESTAMP_FORMAT), row[2]])
                    else:
                        writer.writerow(row)

    @classmethod
    def import_csv(cls, filepath: str):
        """
        Imports notes from a CSV file.
        """
        import csv
        with open(filepath, 'r') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            for row in reader:
                row_dict = dict(zip(headers, row))
                extracted_note_text = row_dict.get('note_text')
                if not extracted_note_text:
                    logger.warning(f"Skipping row with missing note_text: {row}")
                    continue
                note_text = str(extracted_note_text)
                processed_note_text = row_dict.get('processed_note_text') or ""
                processing_error = row_dict.get('processing_error') or ""
                timestamp_str = row_dict.get('timestamp')
                if timestamp_str:
                    timestamp: Optional[datetime] = datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)
                else: 
                    timestamp = None
                if timestamp is not None:
                    new_note = cls.create(
                        note_text=note_text,
                        timestamp=timestamp,
                        processed_note_text=processed_note_text,
                    )
                else:
                    new_note = cls.create(
                        note_text=note_text,
                        processed_note_text=processed_note_text,
                    )
                if processing_error:
                    new_note.processing_error = processing_error
                    new_note.save()



