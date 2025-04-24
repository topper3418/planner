import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, PrivateAttr, ValidationError

from ..config import TIMESTAMP_FORMAT
from ..util import parse_time
from .annotation import Annotation
from .connection import get_connection


logger = logging.getLogger(__name__)


class Action(BaseModel):
    """
    Represents an action that the user took
    """
    id: int = Field(..., description="Unique identifier for the action")
    start_time: datetime = Field(..., description="Start time of the action")
    action_text: str = Field(..., description="Text of the action")
    source_annotation_id: int = Field(..., description="ID of the source annotation")
    todo_id: Optional[int] = Field(None, description="ID of the todo associated with the action")
    mark_complete: bool = Field(False, description="True if the action marks the todo as complete")

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
        Returns the SQL query to create the actions table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
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
            start_time=parse_time(row[1]),
            action_text=row[2],
            source_annotation_id=row[3],
            todo_id=row[4],
            mark_complete=bool(row[5]),
        )

    @classmethod
    def get_by_id(cls, action_id: int) -> Optional["Action"]:
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

    @classmethod
    def get_by_source_annotation_id(cls, annotation_id: int) -> Optional["Action"]:
        """
        Retrieves actions by source annotation ID.
        """
        query = '''
            SELECT * FROM actions WHERE source_annotation_id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (annotation_id,))
            row = cursor.fetchone()
            print(f'fetched row for action by annotation id {annotation_id}', row)
            if row:
                return cls.from_sqlite_row(row)
            else:
                return None

    @classmethod
    def get_by_todo_complete(cls, todo_id: int) -> Optional["Action"]:
        """
        Retrieves actions by todo ID and completion status.
        """
        query = '''
            SELECT * FROM actions WHERE todo_id = ? AND mark_complete = 1
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (todo_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_sqlite_row(row)
            else:
                return None

    def refresh(self):
        copy = self.get_by_id(self.id)
        if copy:
            self.start_time = copy.start_time
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
            SET start_time = ?, action_text = ?, todo_id = ?, mark_complete = ?
            WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                datetime.strftime(self.start_time, TIMESTAMP_FORMAT),
                self.action_text,
                self.todo_id,
                int(self.mark_complete),
                self.id,
            ))
            conn.commit()

    @classmethod
    def create(
            cls, 
            action_text: str, 
            start_time: str | datetime, 
            source_annotation_id: int, 
            todo_id: Optional[int] = None, 
            mark_complete: bool = False
    ):
        """
        Creates a new action in the database.
        """
        query = '''
            INSERT INTO actions (start_time, action_text, source_annotation_id, todo_id, mark_complete)
            VALUES (?, ?, ?, ?, ?)
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                start_time if isinstance(start_time, str) else datetime.strftime(start_time, TIMESTAMP_FORMAT),
                action_text, 
                source_annotation_id, 
                todo_id, 
                mark_complete
            ))
            conn.commit()
            action_id = cursor.lastrowid
        if action_id is None:
            raise ValueError("Failed to create action in the database.")
        try:
            action = cls.get_by_id(action_id)
        except ValidationError as e:
            logger.error(f"Failed to create action: {e}")
            raise
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
    def get_all(
            cls,
            before: Optional[str | datetime] = None,
            after: Optional[str | datetime] = None,
            search: Optional[str] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 25,
            applied_to_todo: Optional[bool] = None,
    ):
        """
        Reads actions from the database.
        """
        query = '''
            SELECT * FROM actions
            WHERE 1=1
        '''
        params = []
        # build the query dynamically
        if before:
            query += ' AND start_time < ?'
            if isinstance(before, datetime):
                before = datetime.strftime(before, TIMESTAMP_FORMAT)
            params.append(before)
        if after:
            query += ' AND start_time > ?'
            if isinstance(after, datetime):
                after = datetime.strftime(after, TIMESTAMP_FORMAT)
            params.append(after)
        if search:
            query += ' AND action_text LIKE ?'
            params.append(f'%{search}%')
        if applied_to_todo is not None:
            # if true, only show actions where the todoid is not null
            if applied_to_todo:
                query += ' AND todo_id IS NOT NULL'
            else:
                query += ' AND todo_id IS NULL'
        # apply offset,  limit an order
        query += ' ORDER BY start_time DESC LIMIT ? OFFSET ?'
        params.append(limit)
        params.append(offset)
        # run query and return results
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [cls.from_sqlite_row(row) for row in rows]

    @classmethod
    def find_by_annotation_id(cls, annotation_id: int) -> Optional["Action"]:
        """
        Finds actions by annotation ID.
        """
        query = '''
            SELECT * FROM actions WHERE source_annotation_id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (annotation_id,))
            rows = cursor.fetchone()
            if rows:
                return cls.from_sqlite_row(rows)
            else:
                return None




