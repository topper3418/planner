import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr, ValidationError

from ..config import TIMESTAMP_FORMAT
from ..util import format_time, parse_time
from .annotation import Annotation
from .connection import get_connection


logger = logging.getLogger(__name__)


class Curiosity(BaseModel):
    """
    Represents a curiosity that the user took
    """
    id: int = Field(..., description="Unique identifier for the curiosity")
    curiosity_text: str = Field(..., description="Text of the curiosity")
    source_annotation_id: int = Field(..., description="ID of the source annotation")

    _source_annotation: Optional[Annotation] = PrivateAttr(default=None)
    @property
    def source_annotation(self) -> Annotation:
        """
        Returns the note associated with the action. """
        if self._source_annotation is None:
            self._source_annotation = Annotation.get_by_id(self.source_annotation_id)
            if self._source_annotation is None:
                logger.error(f"Annotation with ID {self.source_annotation_id} not found in the database.")
                raise ValueError(f"Annotation with ID {self.source_annotation_id} not found in the database.")
        return self._source_annotation
    @source_annotation.setter
    def source_annotation(self, note: Annotation):
        if not note.id == self.source_annotation_id:
            raise ValueError("note ID does not match source_annotation_id")
        self._source_annotation = note

    @classmethod
    def ensure_table(cls):
        """
        ensures the table exists in the db
        """
        query = '''
            CREATE TABLE IF NOT EXISTS curiosities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                curiosity_text TEXT NOT NULL,
                source_annotation_id INTEGER NOT NULL,
                FOREIGN KEY (source_annotation_id) REFERENCES annotations(id)
            )
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def from_sqlite_row(cls, row):
        """
        Creates a Curiosity object from a SQLite row.
        """
        return cls(
            id=row[0],
            curiosity_text=row[1],
            source_annotation_id=row[2]
        )

    @classmethod
    def get_by_id(cls, id: int) -> Optional["Curiosity"]:
        """
        Returns a Curiosity object by its ID.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM curiosities WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                return cls.from_sqlite_row(row)
            return None

    @classmethod
    def get_by_source_annotation_id(cls, source_annotation_id: int) -> Optional["Curiosity"]:
        """
        Returns a Curiosity object by its source annotation ID.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM curiosities WHERE source_annotation_id = ?", (source_annotation_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_sqlite_row(row)
            return None

    def refresh(self):
        copy = self.get_by_id(self.id)
        if copy:
            self.curiosity_text = copy.curiosity_text
            self.source_annotation_id = copy.source_annotation_id
            self._source_annotation = copy._source_annotation
        else:
            raise ValueError(f"Curiosity with ID {self.id} not found in the database.")

    def save(self):
        """
        Saves the Curiosity object to the database.
        """
        if not self.id:
            query = '''
                INSERT INTO curiosities (curiosity_text, source_annotation_id)
                VALUES (?, ?)
            '''
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self.curiosity_text, self.source_annotation_id))
                if cursor.lastrowid is None:
                    raise ValueError("Failed to insert curiosity into the database.")
                self.id = cursor.lastrowid
                conn.commit()
        else:
            query = '''
                UPDATE curiosities
                SET curiosity_text = ?, source_annotation_id = ?
                WHERE id = ?
            '''
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (self.curiosity_text, self.source_annotation_id, self.id))
                conn.commit()

    @classmethod
    def create(
            cls, 
            curiosity_text: str, 
            source_annotation_id: int
    ) -> "Curiosity":
        """
        Creates a new Curiosity object and saves it to the database.
        """
        curiosity = cls(
            id=None,
            curiosity_text=curiosity_text,
            source_annotation_id=source_annotation_id
        )
        curiosity.save()
        return curiosity

    def delete(self):
        """
        Deletes the Curiosity object from the database.
        """
        if not self.id:
            raise ValueError("Curiosity ID is not set.")
        query = '''
            DELETE FROM curiosities WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.id,))
            conn.commit()

    @classmethod
    def get_all(
            cls,
            before: Optional[str | datetime] = None,
            after: Optional[str | datetime] = None,
            search: Optional[str] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 15,
    ) -> List["Curiosity"]:
        """
        Returns a list of all Curiosity objects in the database.
        """
        query = '''
            SELECT
                curiosities.id,
                curiosities.curiosity_text,
                curiosities.source_annotation_id
            FROM curiosities
            JOIN annotations ON curiosities.source_annotation_id = annotations.id
            JOIN notes ON annotations.note_id = notes.id
        '''
        args = []
        query += " WHERE 1=1"
        if before:
            if isinstance(before, datetime):
                before = format_time(before)
            query += " AND notes.created_at < ?"
            args.append(before)
        if after:
            if isinstance(after, datetime):
                after = format_time(after)
            query += " AND notes.created_at > ?"
            args.append(after)
        if search:
            query += " AND curiosities.curiosity_text LIKE ?"
            args.append(f"%{search}%")
        query += " ORDER BY notes.created_at DESC"
        query += " LIMIT ? OFFSET ?"
        args.append(limit)
        args.append(offset)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            rows = cursor.fetchall()
            return [cls.from_sqlite_row(row) for row in rows]


