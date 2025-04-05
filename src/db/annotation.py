import sqlite3
from pydantic import BaseModel, Field

from src.config import NOTES_DATABASE_FILEPATH


class Annotation(BaseModel):
    """
    Represents an annotation from an LLM model. 
    Refrences a note and a tag.
    the LLM will add an annotation that re-frames the note around the tag
    """
    id: int = Field(..., description="Unique identifier for the annotation")
    note_id: int = Field(..., description="Unique identifier for the note")
    tag_id: int = Field(..., description="Unique identifier for the tag")
    annotation_text: str = Field(..., description="The note reframed around the tag") 

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the annotations table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                annotation_text TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            )
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def create(cls, note_id: int, tag_id: int, annotation_text: str):
        """
        Creates a new annotation in the database.
        """
        query = '''
            INSERT INTO annotations (note_id, tag_id, annotation_text) VALUES (?, ?, ?)
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (note_id, tag_id, annotation_text))
            conn.commit()
            if cursor.lastrowid is None:
                raise ValueError("Failed to create annotation")
            return cls(id=cursor.lastrowid, note_id=note_id, tag_id=tag_id, annotation_text=annotation_text)

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
            return [cls(id=row[0], note_id=row[1], tag_id=row[2], annotation_text=row[3]) for row in rows]

    @classmethod
    def get_annotations_for_tag(cls, tag_id: int, limit: int = 50):
        """
        Retrieves all annotations for a given tag.
        """
        query = '''
            SELECT * FROM annotations WHERE tag_id = ? LIMIT ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (tag_id,))
            rows = cursor.fetchall()
            return [cls(id=row[0], note_id=row[1], tag_id=row[2], annotation_text=row[3]) for row in rows]
