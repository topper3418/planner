from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, Field, PrivateAttr


from ..logging import get_logger
from ..util import format_time
from .note import Note
from .connection import get_connection


if TYPE_CHECKING:
    from .tool_call import ToolCall

logger = get_logger(__name__)


class Curiosity(BaseModel):
    """
    Represents a curiosity that the user took
    """

    id: int = Field(..., description="Unique identifier for the curiosity")
    curiosity_text: str = Field(..., description="Text of the curiosity")
    source_note_id: int = Field(..., description="ID of the source note")

    _source_note: Optional[Note] = PrivateAttr(default=None)

    @property
    def source_note(self) -> Note:
        """
        Returns the note associated with the action."""
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
    def source_note(self, note: Note):
        if not note.id == self.source_note_id:
            raise ValueError("note ID does not match source_annotation_id")
        self._source_note = note

    @property
    def tool_calls(self) -> List["ToolCall"]:
        """
        Returns the tool calls associated with the action.
        """
        from .tool_call import ToolCall

        return ToolCall.get_by_target("curiosities", self.id)

    @classmethod
    def ensure_table(cls):
        """
        ensures the table exists in the db
        """
        query = """
            CREATE TABLE IF NOT EXISTS curiosities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                curiosity_text TEXT NOT NULL,
                source_note_id INTEGER NOT NULL,
                FOREIGN KEY (source_note_id) REFERENCES note(id)
            )
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def from_sqlite_row(cls, row):
        """
        Creates a Curiosity object from a SQLite row.
        """
        return cls(id=row[0], curiosity_text=row[1], source_note_id=row[2])

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
    def get_by_source_note_id(
        cls, source_note_id: int
    ) -> List["Curiosity"]:
        """
        Returns a Curiosity object by its source annotation ID.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM curiosities WHERE source_note_id = ?",
                (source_note_id,),
            )
            rows = cursor.fetchall()
            return (
                [cls.from_sqlite_row(row) for row in rows] if rows else []
            )

    def refresh(self):
        copy = self.get_by_id(self.id)
        if copy:
            self.curiosity_text = copy.curiosity_text
            self.source_note_id = copy.source_note_id
            self._source_note = copy._source_note
        else:
            raise ValueError(
                f"Curiosity with ID {self.id} not found in the database."
            )

    def save(self):
        """
        Saves the Curiosity object to the database.
        """
        if not self.id:
            query = """
                INSERT INTO curiosities (curiosity_text, source_note_id)
                VALUES (?, ?)
            """
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query, (self.curiosity_text, self.source_note_id)
                )
                if cursor.lastrowid is None:
                    raise ValueError(
                        "Failed to insert curiosity into the database."
                    )
                self.id = cursor.lastrowid
                conn.commit()
        else:
            query = """
                UPDATE curiosities
                SET curiosity_text = ?, source_note_id = ?
                WHERE id = ?
            """
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    query,
                    (self.curiosity_text, self.source_note_id, self.id),
                )
                conn.commit()

    @classmethod
    def create(
        cls, curiosity_text: str, source_note_id: int
    ) -> "Curiosity":
        """
        Creates a new Curiosity object and saves it to the database.
        """
        curiosity = cls(
            id=0,
            curiosity_text=curiosity_text,
            source_note_id=source_note_id,
        )
        curiosity.save()
        return curiosity

    def delete(self):
        """
        Deletes the Curiosity object from the database.
        """
        if not self.id:
            raise ValueError("Curiosity ID is not set.")
        query = """
            DELETE FROM curiosities WHERE id = ?
        """
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
        query = """
            SELECT
                curiosities.id,
                curiosities.curiosity_text,
                curiosities.source_note_id
            FROM curiosities
            JOIN notes ON curiosities.source_note_id = notes.id
        """
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
