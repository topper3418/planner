from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr

from ..logging import get_logger

from .note import Note
from .connection import get_connection


logger = get_logger(__name__)


class ToolCall(BaseModel):
    """
    Represents a tool call from a user's note'
    """

    id: int = Field(..., description="Unique identifier for the tool call")
    source_note_id: int = Field(..., description="ID of the source note")
    error_text: str = Field(
        ..., description="Error message if the tool call fails in some way"
    )
    target_table: str = Field(
        ..., description="name of table of the object being modified"
    )
    target_id: int = Field(
        ..., description="ID of the object being modified"
    )
    target: Optional[str] = Field(
        ...,
        description="JSON dump of the object before modification (if applicable)",
    )
    tool_call: str = Field(
        ..., description="JSON dump of the tool call for the function"
    )

    _source_note: Optional[Note] = PrivateAttr(default=None)

    @property
    def source_note(self) -> Note:
        """
        Returns the note associated with the tool call.
        """
        if self._source_note is None:
            self._source_note = Note.get_by_id(self.source_note_id)
            if self._source_note is None:
                logger.error(
                    f"Note with ID {self.source_note_id} not found in the database."
                )
                raise ValueError(
                    f"Note with ID {self.source_note_id} not found in the database."
                )
        return self._source_note

    @source_note.setter
    def source_note(self, Note: Note):
        if not Note.id == self.source_note_id:
            raise ValueError("note ID does not match source_note_id")
        self._source_note = Note

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the tool calls table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS tool_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_note_id INTEGER NOT NULL,
                error_text TEXT,
                target_table TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                target TEXT,
                tool_call TEXT NOT NULL,
                FOREIGN KEY (source_note_id) REFERENCES notes (id)
            )
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def from_sqlite_row(cls, row):
        """
        Creates a tool call instance from a SQLite row.
        """
        return cls(
            id=row[0],
            source_note_id=row[1],
            error_text=row[2],
            target_table=row[3],
            target_id=row[4],
            target=row[5],
            tool_call=row[6],
        )

    @classmethod
    def get_by_id(cls, tool_call_id: int) -> Optional["ToolCall"]:
        """
        Retrieves a tool call instance by its ID.
        """
        query = """
            SELECT * FROM tool_calls WHERE id = ?
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (tool_call_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return cls.from_sqlite_row(row)

    @classmethod
    def get_by_source_note_id(cls, note_id: int) -> List["ToolCall"]:
        """
        Retrieves a tool call instance by its source annotation ID.
        """
        query = """
            SELECT * FROM tool_calls WHERE source_note_id = ?
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (note_id,))
            rows = cursor.fetchall()
            return (
                [cls.from_sqlite_row(row) for row in rows] if rows else []
            )

    @classmethod
    def get_by_target(
        cls, target_table: str, target_id: int
    ) -> List["ToolCall"]:
        """
        Retrieves a tool call instance by its target table and target ID.
        """
        query = """
            SELECT * FROM tool_calls WHERE target_table = ? AND target_id = ?
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (target_table, target_id))
            rows = cursor.fetchall()
            return (
                [cls.from_sqlite_row(row) for row in rows] if rows else []
            )

    def refresh(self):
        """
        Refreshes the tool call instance by reloading it from the database.
        """
        copy = self.get_by_id(self.id)
        if copy:
            self.source_note_id = copy.source_note_id
            self.error_text = copy.error_text
            self.target_table = copy.target_table
            self.target_id = copy.target_id
            self.target = copy.target
            self.tool_call = copy.tool_call
        else:
            logger.error(
                f"tool call with ID {self.id} not found in the database."
            )
            raise ValueError(
                f"tool call with ID {self.id} not found in the database."
            )

    def save(self):
        """
        Saves the tool call instance to the database.
        """
        query = """
            UPDATE tool_calls
            SET source_note_id = ?, error_text = ?, target_table = ?, target_id = ?, target = ?, tool_call = ?
            WHERE id = ?
        """
        args = (
            self.source_note_id,
            self.error_text,
            self.target_table,
            self.target_id,
            self.target,
            self.tool_call,
            self.id,
        )
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

    @classmethod
    def create(
        cls,
        source_note_id: int,
        error_text: str,
        target_table: str,
        target: Optional[str] = None,
        target_id: Optional[int] = None,
        tool_call: str = "",
    ) -> "ToolCall":
        """
        Creates a new tool call instance and saves it to the database.
        """
        query = """
            INSERT INTO tool_calls (source_note_id, error_text, target_table, target_id, target, tool_call)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        args = (
            source_note_id,
            error_text,
            target_table,
            target,
            target_id,
            tool_call,
        )
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()
            if cursor.lastrowid is None:
                logger.error(
                    f"Failed to create tool call for source note ID {source_note_id}."
                )
                raise ValueError(
                    f"Failed to create tool call for source note ID {source_note_id}."
                )
            return cls(
                id=cursor.lastrowid,
                source_note_id=source_note_id,
                error_text=error_text,
                target_table=target_table,
                target=target,
                tool_call=tool_call,
            )
