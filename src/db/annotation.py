import sqlite3
from pydantic import BaseModel, Field

from src.config import NOTES_DATABASE_FILEPATH
from src.db import category


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
            return cls(id=cursor.lastrowid, note_id=note_id, category_id=category_id, annotation_text=annotation_text)

    @classmethod
    def get_annotations_for_note(cls, note_id: int):
        """
        Retrieves all annotations for a given note.
        """
        query = '''
            SELECT * FROM annotations WHERE note_id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (note_id,))
            rows = cursor.fetchall()
            return [cls(id=row[0], note_id=row[1], category_id=row[2], annotation_text=row[3]) for row in rows]
