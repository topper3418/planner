import sqlite3
from typing import ClassVar, List, Optional

from pydantic import BaseModel, Field, PrivateAttr

from src.config import NOTES_DATABASE_FILEPATH
from .category import Category
from .note import Note


class Annotation(BaseModel):
    """
    Represents an annotation from an LLM model. 
    Refrences a note and a category.
    the LLM will add an annotation that re-frames the note around the category
    """
    id: int = Field(..., description="Unique identifier for the annotation")
    note_id: int = Field(..., description="Unique identifier for the note")
    category_id: int = Field(..., description="Unique identifier for the category")
    annotation_text: str = Field(..., description="The note reframed around the category") 
    reprocess: bool = Field(False, description="True if the annotation needs to be reprocessed")
    
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

    _category: Optional[Category] = PrivateAttr(default=None)
    @property
    def category(self) -> Category:
        """
        Returns the category associated with the annotation.
        """
        if self._category is None:
            self._category = Category.get_by_id(self.category_id)
            if self._category is None:
                raise ValueError(f"Category with ID {self.category_id} not found")
        return self._category
    @category.setter
    def category(self, category: Category):
        """
        Sets the category associated with the annotation.
        """
        if not isinstance(category, Category):
            raise ValueError("category must be an instance of Category")
        self._category = category
        self.category_id = category.id

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the annotations table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                annotation_text TEXT NOT NULL,
                reprocess INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (note_id) REFERENCES notes(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def create(cls, note_id: int, category_id: int, annotation_text: str):
        """
        Creates a new annotation in the database.
        """
        query = '''
            INSERT INTO annotations (note_id, category_id, annotation_text) VALUES (?, ?, ?)
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (note_id, category_id, annotation_text))
            conn.commit()
            if cursor.lastrowid is None:
                raise ValueError("Failed to create annotation")
            return cls.get_by_id(cursor.lastrowid)

    def save(self):
        """
        Updates the annotation in the database.
        """
        query = '''
            UPDATE annotations SET category_id = ?, annotation_text = ?, reprocess = ? WHERE id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.category_id, self.annotation_text, self.reprocess, self.id))
            conn.commit()

    @classmethod
    def from_sqlite_row(cls, row):
        """
        Converts a SQLite row to an Annotation instance.
        """
        return cls(
            id=row[0],
            note_id=row[1],
            category_id=row[2],
            annotation_text=row[3],
            reprocess=bool(row[4]),
        )

    @ classmethod
    def get_by_id(cls, annotation_id: int):
        """
        Retrieves an annotation by its ID.
        """
        query = '''
            SELECT * FROM annotations WHERE id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
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
            self.category_id = copy.category_id
            self.annotation_text = copy.annotation_text
            self.reprocess = copy.reprocess
            self._note = None
            self._category = None
        else:
            raise ValueError(f"Annotation with ID {self.id} not found in the database.")

    @classmethod
    def get_by_note_id(cls, note_id: int):
        """
        Retrieves all annotations for a given note.
        """
        query = '''
            SELECT * FROM annotations WHERE note_id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (note_id,))
            row = cursor.fetchone()
            return cls.from_sqlite_row(row) if row else None

    @classmethod
    def get_by_category_name(
            cls, 
            category_name: str,
            before: Optional[str] = None,
            after: Optional[str] = None,
            limit: Optional[int] = None,
            search: Optional[str] = None,
    ) -> List["Annotation"]:
        """
        Retrieves all annotations for a given category.
        """
        # make sure the category is authentic
        category = Category.find_by_name(category_name)
        if category is None:
            raise ValueError(f"Category with name '{category_name}' not found")
        query = 'SELECT annotations.id, annotations.note_id, annotations.category_id, annotations.annotation_text, annotations.reprocess FROM annotations'
        args: list = []
        if before or after:
            query += ' JOIN notes ON annotations.note_id = notes.id'
        if before:
            query += ' AND notes.timestamp < ?'
            args.append(before)
        if after:
            query += ' AND notes.timestamp > ?'
            args.append(after)
        if search:
            query += ' AND annotations.annotation_text LIKE ?'
            args.append(f'%{search}%')
        if limit:
            query += ' LIMIT ?'
            args.append(limit)
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (category.id,))
            rows = cursor.fetchall()
            return [cls.from_sqlite_row(row) for row in rows] if rows else []
    
    def delete(self):
        """
        Deletes the annotation from the database.
        """
        query = '''
            DELETE FROM annotations WHERE id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.id,))
            conn.commit()

    @classmethod
    def get_next_reprocess_candidate(cls):
        """
        Returns the SQL query to fetch the next unprocessed annotation.
        """
        query = '''
            SELECT * FROM annotations WHERE reprocess = 1
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            unprocessed_annotation = cursor.fetchone()
            if unprocessed_annotation:
                return cls.from_sqlite_row(unprocessed_annotation)
            else:
                return None


