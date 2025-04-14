import sqlite3
import logging
from typing import Optional
from pydantic import BaseModel, Field, PrivateAttr

from src.config import NOTES_DATABASE_FILEPATH
from .annotation import Annotation


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
    source_annotation_id: int = Field(..., description="ID of the source annotation")
    todo_id: Optional[int] = Field(None, description="ID of the todo associated with the action")
    mark_complete: bool = Field(False, description="True if the action marks the todo as complete")

    _source_annotation: Optional[Annotation] = PrivateAttr(default=None)
    @property
    def source_annotation(self) -> Annotation:
        """
        Returns the note associated with the action.
        """
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
        Returns the SQL query to create the actions table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME DEFAULT NULL,
                action_text TEXT NOT NULL,
                source_annotation_id INTEGER NOT NULL,
                todo_id INTEGER DEFAULT NULL,
                mark_complete INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (source_annotation_id) REFERENCES annotations(id),
                FOREIGN KEY (todo_id) REFERENCES todos(id)
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
            source_annotation_id=row[4],
            todo_id=row[5],
            mark_complete=bool(row[6]),
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
            self.todo_id = copy.todo_id
            self.mark_complete = copy.mark_complete
        else:
            logger.error(f"Action with ID {self.id} not found in the database.")

    def save(self):
        """
        Saves the action to the database.
        """
        query = '''
            UPDATE actions
            SET start_time = ?, end_time = ?, action_text = ?, todo_id = ?, mark_complete = ?
            WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                self.start_time,
                self.end_time,
                self.action_text,
                self.todo_id,
                int(self.mark_complete),
                self.id,
            ))
            conn.commit()

    @classmethod
    def create(cls, action_text: str, start_time: str, source_annotation_id: int, end_time: Optional[str] = None, todo_id: Optional[int] = None, mark_complete: bool = False):
        """
        Creates a new action in the database.
        """
        query = '''
            INSERT INTO actions (start_time, end_time, action_text, source_annotation_id, todo_id, mark_complete)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (start_time, end_time, action_text, source_annotation_id, todo_id, mark_complete))
            conn.commit()
            action_id = cursor.lastrowid
        if action_id is None:
            raise ValueError("Failed to create action in the database.")
        action = cls.get_by_id(action_id)
        return action

    def delete(self):
        """
        Deletes the action from the database.
        """
        # first, mark the todo as incomplete if applicable
        if self.todo_id and self.mark_complete:
            todo_query = '''
                UPDATE todos SET complete = 0 WHERE id = ?
            '''
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(todo_query, (self.todo_id,))
                conn.commit()
        query = '''
            DELETE FROM actions WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.id,))
            conn.commit()

    @classmethod
    def read(
            cls,
            before: Optional[str] = None,
            after: Optional[str] = None,
            search: Optional[str] = None,
            limit: Optional[int] = None,
    ):
        """
        Reads actions from the database.
        """
        query = '''
            SELECT * FROM actions
            WHERE 1=1
        '''
        params = []
        if before:
            query += ' AND start_time < ?'
            params.append(before)
        if after:
            query += ' AND start_time > ?'
            params.append(after)
        if search:
            query += ' AND action_text LIKE ?'
            params.append(f'%{search}%')
        query += ' ORDER BY id DESC'
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [cls.from_sqlite_row(row) for row in rows]





