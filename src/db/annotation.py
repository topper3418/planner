from datetime import datetime
from typing import List, Optional
import logging

from pydantic import BaseModel, Field, PrivateAttr

from .note import Note
from .connection import get_connection
from ..util import format_time

logger = logging.getLogger(__name__)


class Annotation(BaseModel):
    """
    Represents an annotation from an LLM model. 
    Refrences a note. This object is optimized for creating LLM summaries after the fact
    """
    id: int = Field(..., description="Unique identifier for the annotation")
    note_id: int = Field(..., description="Unique identifier for the note")
    annotation_text: str = Field(..., description="The note reframed around the category") 
    
    _note: Optional[Note] = PrivateAttr(default=None)
    @property
    def note(self) -> Note:
        """
        Returns the note associated with the annotation.
        """
        if self._note is None:
            self._note = Note.get_by_id(self.note_id)
            if self._note is None:
                raise ValueError(f"Note with ID {self.note_id} not found")
        return self._note
    @note.setter
    def note(self, note: Note):
        """
        Sets the note associated with the annotation.
        """
        if not isinstance(note, Note):
            raise ValueError("note must be an instance of Note")
        self._note = note
        self.note_id = note.id

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the annotations table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                annotation_text TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id)
            )
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def create(cls, note_id: int, annotation_text: str):
        """
        Creates a new annotation in the database.
        """
        query = '''
            INSERT INTO annotations (note_id, annotation_text) VALUES (?, ?)
        '''
        args = (note_id, annotation_text)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()
            if cursor.lastrowid is None:
                raise ValueError("Failed to create annotation")
            return cls.get_by_id(cursor.lastrowid)

    def save(self):
        """
        Updates the annotation in the database.
        """
        query = '''
            UPDATE annotations SET annotation_text = ?, reprocess = ? WHERE id = ?
        '''
        args = (self.annotation_text, self.id)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

    def reload(self):
        """
        Reloads the annotation from the database.
        """
        query = '''
            SELECT * FROM annotations WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.id,))
            row = cursor.fetchone()
            if row:
                self.id, self.note_id, self.annotation_text = row
                self._note = None
                self._category = None
            else:
                raise ValueError(f"Annotation with ID {self.id} not found")

    @classmethod
    def from_sqlite_row(cls, row):
        """
        Converts a SQLite row to an Annotation instance.
        """
        return cls(
            id=row[0],
            note_id=row[1],
            annotation_text=row[2]
        )

    @ classmethod
    def get_by_id(cls, annotation_id: int):
        """
        Retrieves an annotation by its ID.
        """
        query = '''
            SELECT * FROM annotations WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (annotation_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_sqlite_row(row)
            else:
                raise ValueError(f"Annotation with ID {annotation_id} not found")

    def refresh(self):
        """
        Refreshes the Annotation instance by reloading it from the database.
        """
        copy = self.get_by_id(self.id)
        if copy:
            self.annotation_text = copy.annotation_text
            self._note = None
        else:
            raise ValueError(f"Annotation with ID {self.id} not found in the database.")

    @classmethod
    def get_by_source_note_id(cls, note_id: int):
        """
        Retrieves all annotations for a given note.
        """
        query = '''
            SELECT * FROM annotations WHERE note_id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (note_id,))
            row = cursor.fetchone()
            return cls.from_sqlite_row(row) if row else None

    def delete(self):
        """
        Deletes the annotation from the database.
        """
        query = '''
            DELETE FROM annotations WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.id,))
            conn.commit()

    @classmethod
    def get_all(cls, before: Optional[str | datetime] = None, after: Optional[str | datetime] = None, search: Optional[str] = None, offset: int = 0, limit: int = 25):
        """
        Retrieves all annotations from the database.
        """
        query = '''
            SELECT annotations.id, annotations.note_id, annotations.annotation_text FROM annotations
        '''
        params = []
        # build the query dynamically
        if before or after:
            query += ' JOIN notes ON annotations.note_id = notes.id'
        query += ' WHERE 1=1'
        if before:
            query += ' AND notes.timestamp < ?'
            if isinstance(before, datetime):
                before = format_time(before)
            params.append(before)
        if after:
            query += ' AND notes.timestamp > ?'
            if isinstance(after, datetime):
                after = format_time(after)
            params.append(after)
        if search:
            query += ' AND annotations.annotation_text LIKE ?'
            params.append(f'%{search}%')
        # apply offset, limit and order
        query += ' ORDER BY annotations.id DESC LIMIT ? OFFSET ?'
        params.append(limit)
        params.append(offset)
        # run query and return results
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [cls.from_sqlite_row(row) for row in rows] if rows else []


