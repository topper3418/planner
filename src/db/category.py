import sqlite3
from pydantic import BaseModel, Field

from src.config import NOTES_DATABASE_FILEPATH


class Category(BaseModel):
    """
    Represents a toipc for M2M grouping notes
    """
    id: int = Field(..., description="Unique identifier for the category")
    name: str = Field(..., description="Name of the category")
    description: str = Field(..., description="Description of the category")
    color: str = Field(..., description="Color of the category")

    @classmethod
    def ensure_table(cls):
        """
        Returns the SQL query to create the category table.
        """
        query = '''
            CREATE TABLE IF NOT EXISTS categories (
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
        Updates the category in the database.
        """
        query = '''
            UPDATE categories SET name = ?, description = ?, color = ? WHERE id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.name, self.description, self.color, self.id))
            conn.commit()

    @classmethod
    def create(cls, name, description=None, color=None):
        """
        Creates a new category in the database.
        """
        query = '''
            INSERT INTO categories (name, description, color) VALUES (?, ?, ?)
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name, '', ''))
            conn.commit()
            if cursor.lastrowid is None:
                raise ValueError("Failed to create category")
            category = cls(id=cursor.lastrowid, name=name, description='', color='')
            # less common, likely just for the default inserts
            if description or color:
                if description:
                    category.description = description
                if color:
                    category.color = color
                category.save()
            return category

    @classmethod
    def get_all(cls):
        """
        Reads all categories from the database.
        """
        query = '''
            SELECT * FROM categories
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [cls(id=row[0], name=row[1], description=row[2], color=row[3]) for row in rows]

    @classmethod
    def get_by_id(cls, category_id):
        """
        Fetches a category by its ID.
        """
        query = '''
            SELECT * FROM categories WHERE id = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (category_id,))
            row = cursor.fetchone()
            if row:
                return cls(id=row[0], name=row[1], description=row[2], color=row[3])
            return None

    @classmethod
    def find_by_name(cls, name) -> "Category":
        """
        Finds a category by its name.
        """
        query = '''
            SELECT * FROM categories WHERE name = ?
        '''
        with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Category with name '{name}' not found")
            return cls(id=row[0], name=row[1], description=row[2], color=row[3])


default_categories = [
    Category(
        id=0, 
        name="action", 
        description="Documents an action taken by the user. Anything the user says they did, or anything the user says they are about to do in the immediate future This pertains to an action that was taken, not a task to be completed. It also excludes something that seems like an action, but is actually an observation. This does include future tense actions that sounds like I am going to do it immediately. For example, I am -> action, I just -> action, I will later -> not an action", 
        color="blue"
    ),
    Category(
        id=0, 
        name="todo", 
        description="Indicates a user's intention to complete a task. It is the intent to do an an action", 
        color="cyan"
    ),
    Category(
        id=0, 
        name="curiosity", 
        description="Something the user is curious about, or wants to learn more about. This can be a wondering, or a direct question to the system. I wonder, I am curious about", 
        color="yellow"
    ),
    Category(
        id=0,
        name="observation",
        description="Documents something the user has learned or observed. Put another way, it is anything the user puts in that is simply storing a thought. This does not include things that the user has done, a user cannot observe their own action. To clarify a grey area, if it seems like the user is observing the result of something they did, it is an observation.",
        color="green"
    ),
    Category(
        id=0,
        name="command",
        description="This is a command from the user to the system. For example, an instruction to change the category of a note directly, or to update an existing todo, updating a note, changing a timeline of something that has already passed. Any time it seems like the user is talking to the system rather than describing something they have done, experienced or need to do is a command",
        color="grey"
    )
]
