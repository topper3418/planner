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


class Todo(BaseModel):
    """
    represents something the user wants to do
    """
    id: int = Field(..., description="Unique identifier for the todo")
    target_start_time: Optional[str] = Field(None, description="Target start time of the todo")
    target_end_time: Optional[str] = Field(None, description="Target end time of the todo")
    todo_text: str = Field(..., description="Text of the todo")
    source_annotation_id: int = Field(..., description="ID of the source annotation")
    complete: bool = Field(False, description="True if the task has been completed")
    cancelled: bool = Field(False, description="True if the task has been cancelled")

    _source_annotation: Optional[Annotation] = PrivateAttr(default=None)
    @property
    def source_annotation(self) -> Annotation:
        """
        Returns the note associated with the todo.
        """
        if self._source_annotation is None:
            self._source_annotation = Annotation.get_by_id(self.source_annotation_id)
            if self._source_annotation is None:
                logger.error(f"Annotation with ID {self.source_annotation_id} not found in the database.")
                raise ValueError(f"Annotation with ID {self.source_annotation_id} not found in the database.")
        return self._source_annotation
    @source_annotation.setter
    def source_annotation(self, annotation: Annotation):
        if not annotation.id == self.source_annotation_id:
            raise ValueError("annotation ID does not match source_note_id")
        self._source_annotation = annotation

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the todos table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_start_time DATETIME DEFAULT NULL,
                target_end_time DATETIME DEFAULT NULL,
                todo_text TEXT NOT NULL,
                source_note_id INTEGER NOT NULL,
                complete INTEGER NOT NULL DEFAULT 0,
                cancelled INTEGER NOT NULL DEFAULT 0
            );
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
    
    @classmethod
    def from_sqlite_row(cls, row) -> "Todo":
        """
        Creates a Todo instance from a SQLite row.
        """
        return cls(
            id=row[0],
            target_start_time=row[1],
            target_end_time=row[2],
            todo_text=row[3],
            source_annotation_id=row[4],
            complete=bool(row[5]),
            cancelled=bool(row[6]),
        )

    @classmethod
    def get_by_id(cls, todo_id: int) -> "Todo":
        """
        Retrieves a Todo instance by its ID.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_sqlite_row(row)
            else:
                logger.error(f"Todo with ID {todo_id} not found in the database.")
                raise ValueError(f"Todo with ID {todo_id} not found in the database.")

    @classmethod
    def get_by_source_annotation_id(cls, source_annotation_id: int) -> "Todo":
        """
        Retrieves a Todo instance by its source annotation ID.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM todos WHERE source_note_id = ?", (source_annotation_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_sqlite_row(row)
            else:
                logger.error(f"Todo with source annotation ID {source_annotation_id} not found in the database.")
                raise ValueError(f"Todo with source annotation ID {source_annotation_id} not found in the database.")

    def refresh(self) -> "Todo":
        """
        Refreshes the Todo instance by reloading it from the database.
        """
        copy = self.get_by_id(self.id)
        self.target_start_time = copy.target_start_time
        self.target_end_time = copy.target_end_time
        self.todo_text = copy.todo_text
        self.complete = copy.complete
        self.cancelled = copy.cancelled
        return self

    def save(self):
        """
        Saves the Todo instance to the database.
        """
        query = '''
            UPDATE todos
            SET target_start_time = ?, target_end_time = ?, todo_text = ?, complete = ?, cancelled = ?
            WHERE id = ?;
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.target_start_time, self.target_end_time, self.todo_text, self.complete, self.cancelled, self.id))
            conn.commit()

    @classmethod
    def get_incomplete(cls, offset=0, limit=15) -> list["Todo"]:
        """
        Retrieves a list of incomplete Todo instances from the database.
        """
        query = '''
            SELECT * FROM todos
            WHERE complete = 0
            LIMIT ?, ?;
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (offset, limit))
            rows = cursor.fetchall()
            return [cls.from_sqlite_row(row) for row in rows]

    @classmethod
    def get_cancelled(self) -> list["Todo"]:
        """
        Retrieves a list of cancelled Todo instances from the database.
        """
        query = '''
            SELECT * FROM todos
            WHERE cancelled = 1;
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self.from_sqlite_row(row) for row in rows]

    @classmethod
    def create(cls, todo_text, source_annotation_id, target_start_time: Optional[str]=None, target_end_time: Optional[str]=None) -> "Todo":
        """
        Creates a new Todo instance and saves it to the database.
        """
        query = '''
            INSERT INTO todos (target_start_time, target_end_time, todo_text, source_note_id)
            VALUES (?, ?, ?, ?);
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (target_start_time, target_end_time, todo_text, source_annotation_id))
            conn.commit()
            last_row_id = cursor.lastrowid
            if last_row_id is None:
                logger.error("Failed to create todo in the database.")
                raise ValueError("Failed to create todo in the database.")
        return cls.get_by_id(last_row_id)

    def delete(self):
        """
        Deletes the Todo instance from the database.
        """
        query = '''
            DELETE FROM todos WHERE id = ?;
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
            complete: Optional[bool] = None,
            cancelled: Optional[bool] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 25,
    ) -> list["Todo"]:
        """
        Reads todos from the database.
        """
        query = '''
            SELECT * FROM todos
        '''
        args = []
        if before:
            query += ' WHERE target_start_time < ?'
            args.append(before)
        if after:
            if 'WHERE' in query:
                query += ' AND target_start_time > ?'
            else:
                query += ' WHERE target_start_time > ?'
            args.append(after)
        if complete is not None:
            if 'WHERE' in query:
                query += ' AND complete = ?'
            else:
                query += ' WHERE complete = ?'
            args.append(int(complete))
        if cancelled is not None:
            if 'WHERE' in query:
                query += ' AND cancelled = ?'
            else:
                query += ' WHERE cancelled = ?'
            args.append(int(cancelled))
        query += ' LIMIT ?, ?'
        args.append(offset)
        args.append(limit)
        with get_connection() as conn:
            cursor = conn.cursor()
            if complete is not None:
                cursor.execute(query, args)
            else:
                cursor.execute(query, args)
            rows = cursor.fetchall()
            return [cls.from_sqlite_row(row) for row in rows]




