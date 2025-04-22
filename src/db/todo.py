import sqlite3
import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, PrivateAttr

from ..config import TIMESTAMP_FORMAT
from ..util import format_time, parse_time
from .annotation import Annotation
from .connection import get_connection


logger = logging.getLogger(__name__)


class Todo(BaseModel):
    """
    represents something the user wants to do
    """
    id: int = Field(..., description="Unique identifier for the todo")
    target_start_time: Optional[datetime] = Field(None, description="Target start time of the todo")
    target_end_time: Optional[datetime] = Field(None, description="Target end time of the todo")
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
            target_start_time=parse_time(row[1]) if row[1] else None,
            target_end_time=parse_time(row[2]) if row[2] else None,
            todo_text=row[3],
            source_annotation_id=row[4],
            complete=bool(row[5]),
            cancelled=bool(row[6]),
        )

    @classmethod
    def get_by_id(cls, todo_id: int) -> Optional["Todo"]:
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
                return None

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
        if copy is None:
            logger.error(f"Todo with ID {self.id} not found in the database.")
            raise ValueError(f"Todo with ID {self.id} not found in the database.")
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
            cursor.execute(query, (
                format_time(self.target_start_time) if self.target_start_time else None, 
                format_time(self.target_end_time) if self.target_end_time else None, 
                self.todo_text, 
                self.complete, 
                self.cancelled, 
                self.id
            ))
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
    def create(cls, todo_text, source_annotation_id, target_start_time: Optional[str | datetime]=None, target_end_time: Optional[str | datetime]=None) -> "Todo":
        """
        Creates a new Todo instance and saves it to the database.
        """
        query = '''
            INSERT INTO todos (target_start_time, target_end_time, todo_text, source_note_id)
            VALUES (?, ?, ?, ?);
        '''
        if isinstance(target_start_time, datetime):
            target_start_time = format_time(target_start_time)
        if isinstance(target_end_time, datetime):
            target_end_time = format_time(target_end_time)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                target_start_time, 
                target_end_time, 
                todo_text, 
                source_annotation_id
            ))
            conn.commit()
            last_row_id = cursor.lastrowid
            if last_row_id is None:
                logger.error("Failed to create todo in the database.")
                raise ValueError("Failed to create todo in the database.")
        created_todo = cls.get_by_id(last_row_id)
        if created_todo is None:
            logger.error(f"Todo with ID {last_row_id} not found in the database.")
            raise ValueError(f"Todo with ID {last_row_id} not found in the database.")
        return created_todo

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
    def get_all(
            cls, 
            before: Optional[datetime | str] = None, 
            after: Optional[datetime | str] = None, 
            complete: Optional[bool] = True,
            cancelled: Optional[bool] = False,
            active: Optional[bool] = True,
            search: Optional[str] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 25,
    ) -> list["Todo"]:
        """
        Reads todos from the database.
        """
        query = '''
            SELECT 
                todos.id, 
                todos.target_start_time, 
                todos.target_end_time, 
                todos.todo_text, 
                todos.source_note_id, 
                todos.complete,
                todos.cancelled
            FROM todos
            JOIN annotations on todos.source_note_id = annotations.id 
            JOIN notes on annotations.note_id = notes.id
        '''
        args = []
        # time range stuff
        if before or after:
            query += ''
            if isinstance(before, datetime):
                before = format_time(before)
            if isinstance(after, datetime):
                after = format_time(after)
        query += ' WHERE 1=1'  # needs this whether or not timing is involved
        if before and after:  # todo scheduled time or todo created time should fall within the range
            query += ' AND (todos.target_start_time BETWEEN ? AND ? OR todos.target_end_time BETWEEN ? AND ? OR notes.timestamp BETWEEN ? AND ?)'
            args.extend([before, after, before, after, before, after])
        elif before:  # todo scheduled time or todo created time should be before the given time
            query += ' AND (todos.target_start_time < ? OR todos.target_end_time < ? OR notes.timestamp < ?)'
            args.extend([before, before, before])
        elif after:  # todo scheduled time or todo created time should be after the given time
            query += ' AND (todos.target_start_time > ? OR todos.target_end_time > ? OR notes.timestamp > ?)'
            args.extend([after, after, after])
        if search:
            query += ' AND (todos.todo_text LIKE ? OR notes.note_text LIKE ? or annotations.annotation_text LIKE ?)'
            args.extend(['%' + search + '%', '%' + search + '%', '%' + search + '%'])
        # filter by status
        # active means not cancelled or complete
        # cancelled means cancelled
        # complete means complete
        # so, 
        if active and complete and cancelled:  # all three
            pass
        if active and complete and not cancelled:  # active and complete
            query += ' AND (todos.cancelled = 0)'
        if active and not complete and cancelled:  # active and cancelled
            query += ' AND (todos.complete = 0)'
        if not active and complete and cancelled:  # complete and cancelled
            query += ' AND (todos.cancelled = 1 or todos.complete = 1)'
        if not active and complete and not cancelled:  # complete only
            query += ' AND (todos.complete = 1)'
        if not active and not complete and cancelled:  # cancelled only
            query += ' AND (todos.cancelled = 1)'
        if active and not complete and not cancelled:  # active only
            query += ' AND (todos.cancelled = 0 and todos.complete = 0)'
        query += ' LIMIT ?, ?'
        args.append(offset)
        args.append(limit)
        print('query: ', query)
        with get_connection() as conn:
            cursor = conn.cursor()
            if complete is not None:
                cursor.execute(query, args)
            else:
                cursor.execute(query, args)
            rows = cursor.fetchall()
            print('rows: ', rows)
            return [cls.from_sqlite_row(row) for row in rows]




