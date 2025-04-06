import sqlite3
from pydantic import BaseModel, Field

from src.config import NOTES_DATABASE_FILEPATH


class Tag(BaseModel):
    """
    Represents a tag for M2M grouping notes
    """
    id: int = Field(..., description="Unique identifier for the tag")
    name: str = Field(..., description="Name of the tag")
    description: str = Field(..., description="Description of the tag")
    color: str = Field(..., description="Color of the tag")

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the tags table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                color TEXT
            )
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def save(self):
        """
        Updates the tag in the database.
        """
        query = '''
            UPDATE tags SET name = ?, description = ?, color = ? WHERE id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.name, self.description, self.color, self.id))
            conn.commit()

    @classmethod
    def create(cls, name, description=None, color=None):
        """
        Creates a new tag in the database.
        """
        query = '''
            INSERT INTO tags (name, description, color) VALUES (?, ?, ?)
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, '', ''))
            conn.commit()
            if cursor.lastrowid is None:
                raise ValueError("Failed to create tag")
            tag = cls(id=cursor.lastrowid, name=name, description='', color='')
            # less common, likely just for the default inserts
            if description or color:
                if description:
                    tag.description = description
                if color:
                    tag.color = color
                tag.save()
            return tag

    @classmethod
    def get_all(cls):
        """
        Reads all tags from the database.
        """
        query = '''
            SELECT * FROM tags
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [cls(id=row[0], name=row[1], description=row[2], color=row[3]) for row in rows]


default_tags = [
    Tag(
        id=0, 
        name="Action", 
        description="Documents an action taken by the user", 
        color="blue"
    ),
    Tag(
        id=0, 
        name="Todo", 
        description="Indicates a user's intention to complete a task", 
        color="lightblue"
    ),
    Tag(
        id=0, 
        name="Curiosity", 
        description="Somewhat like a todo, but for learning or exploration", 
        color="yellow"
    ),
    Tag(
        id=0,
        name="Discovery",
        description="Documents something the user has learned",
        color="green"
    )
]
