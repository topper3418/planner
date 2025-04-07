import sqlite3
from pydantic import BaseModel, Field

from src.config import NOTES_DATABASE_FILEPATH


class Topic(BaseModel):
    """
    Represents a toipc for M2M grouping notes
    """
    id: int = Field(..., description="Unique identifier for the topic")
    name: str = Field(..., description="Name of the topic")
    description: str = Field(..., description="Description of the topic")
    color: str = Field(..., description="Color of the topic")

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the topic table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS topics (
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
        Updates the topic in the database.
        """
        query = '''
            UPDATE topics SET name = ?, description = ?, color = ? WHERE id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.name, self.description, self.color, self.id))
            conn.commit()

    @classmethod
    def create(cls, name, description=None, color=None):
        """
        Creates a new topic in the database.
        """
        query = '''
            INSERT INTO topics (name, description, color) VALUES (?, ?, ?)
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, '', ''))
            conn.commit()
            if cursor.lastrowid is None:
                raise ValueError("Failed to create topic")
            topic = cls(id=cursor.lastrowid, name=name, description='', color='')
            # less common, likely just for the default inserts
            if description or color:
                if description:
                    topic.description = description
                if color:
                    topic.color = color
                topic.save()
            return topic

    @classmethod
    def get_all(cls):
        """
        Reads all topics from the database.
        """
        query = '''
            SELECT * FROM topics
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [cls(id=row[0], name=row[1], description=row[2], color=row[3]) for row in rows]


default_topics = [
    Topic(
        id=0, 
        name="Action", 
        description="Documents an action taken by the user", 
        color="blue"
    ),
    Topic(
        id=0, 
        name="Todo", 
        description="Indicates a user's intention to complete a task", 
        color="lightblue"
    ),
    Topic(
        id=0, 
        name="Curiosity", 
        description="Somewhat like a todo, but for learning or exploration", 
        color="yellow"
    ),
    Topic(
        id=0,
        name="Discovery",
        description="Documents something the user has learned",
        color="green"
    )
]
