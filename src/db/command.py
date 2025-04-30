import logging
from typing import List, Optional
from pydantic import BaseModel, Field, PrivateAttr

from .note import Note
from .connection import get_connection


logger = logging.getLogger(__name__)


class Command(BaseModel):
    """
    Represents a command that the user wants to execute
    """
    id: int = Field(..., description="Unique identifier for the command")
    command_text: str = Field(..., description="Text of the command")
    value_before: str = Field(..., description="Value before the command")
    desired_value: str = Field(..., description="Desired value after the command")
    source_note_id: int = Field(..., description="ID of the source note")
    target_id: int = Field(..., description="ID of the target")

    _source_note: Optional[Note] = PrivateAttr(default=None)
    @property
    def source_note(self) -> Note:
        """
        Returns the note associated with the command.
        """
        if self._source_note is None:
            self._source_note = Note.get_by_id(self.source_note_id)
            if self._source_note is None:
                logger.error(f"Note with ID {self.source_note_id} not found in the database.")
                raise ValueError(f"Note with ID {self.source_note_id} not found in the database.")
        return self._source_note
    @source_note.setter
    def source_note(self, Note: Note):
        if not Note.id == self.source_note_id:
            raise ValueError("note ID does not match source_note_id")
        self._source_note = Note

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the commands table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_text TEXT NOT NULL,
                value_before TEXT NOT NULL,
                desired_value TEXT NOT NULL,
                source_note_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                FOREIGN KEY (source_note_id) REFERENCES note(id)
            );
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @classmethod
    def from_sqlite_row(cls, row):
        """
        Creates a Command instance from a SQLite row.
        """
        return cls(
            id=row[0],
            command_text=row[1],
            value_before=row[2],
            desired_value=row[3],
            source_note_id=row[4],
            target_id=row[5],
        )

    @classmethod
    def get_by_id(cls, command_id: int) -> Optional["Command"]:
        """
        Retrieves a Command instance by its ID.
        """
        query = '''
            SELECT * FROM commands WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (command_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return cls.from_sqlite_row(row)

    @classmethod
    def get_by_source_note_id(cls, annotation_id: int) -> List["Command"]:
        """
        Retrieves a Command instance by its source annotation ID.
        """
        query = '''
            SELECT * FROM commands WHERE source_note_id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (annotation_id,))
            rows = cursor.fetchall()
            return [cls.from_sqlite_row(row) for row in rows] if rows else []
            

    def refresh(self):
        """
        Refreshes the Command instance by reloading it from the database.
        """
        copy = self.get_by_id(self.id)
        if copy:
            self.command_text = copy.command_text
            self.value_before = copy.value_before
            self.desired_value = copy.desired_value
            self.source_note_id = copy.source_note_id
            self._source_note = None
        else:
            logger.error(f"Command with ID {self.id} not found in the database.")
            raise ValueError(f"Command with ID {self.id} not found in the database.")

    def save(self):
        """
        Saves the Command instance to the database.
        """
        query = '''
            UPDATE commands
            SET command_text = ?, value_before = ?, desired_value = ?, source_note_id = ?, target_id = ?
            WHERE id = ?
        '''
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                self.command_text,
                self.value_before,
                self.desired_value,
                self.source_note_id,
                self.target_id,
                self.id
            ))
            conn.commit()

    @classmethod
    def create(
            cls, 
            command_text: str, 
            value_before: str, 
            desired_value: str, 
            source_note_id: int, 
            target_id: int
    ) -> "Command":
        """
        Creates a new command in the database.
        """
        query = '''
            INSERT INTO commands (command_text, value_before, desired_value, source_note_id, target_id) VALUES (?, ?, ?, ?, ?)
        '''
        args = (command_text, value_before, desired_value, source_note_id, target_id)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()
        if cursor.lastrowid is None:
            raise ValueError("Failed to create command")
        command = cls.get_by_id(cursor.lastrowid)
        if command is None:
            raise ValueError("Failed to create command")
        return command

