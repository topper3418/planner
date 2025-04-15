import logging
import sqlite3

from ..config import NOTES_DATABASE_FILEPATH

from .note import Note
from .category import Category, default_categories
from .annotation import Annotation
from .action import Action
from .todo import Todo
from .command import Command

logger = logging.getLogger(__name__)


def ensure_tables():
    logger.debug("ensuring tables...")
    Note.ensure_table()
    Category.ensure_table()
    Annotation.ensure_table()
    Action.ensure_table()
    Todo.ensure_table()
    Command.ensure_table()
    logger.info("tables ensured.")


def teardown():
    with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()
        # Drop all tables
        cursor.execute("DROP TABLE IF EXISTS actions")
        cursor.execute("DROP TABLE IF EXISTS todos")
        cursor.execute("DROP TABLE IF EXISTS commands")
        cursor.execute("DROP TABLE IF EXISTS annotations")
        cursor.execute("DROP TABLE IF EXISTS categories")
        cursor.execute("DROP TABLE IF EXISTS notes")
        conn.commit()

def ensure_default_categories():
    logger.debug("ensuring default categories...")
    for category in default_categories:
        # Check if the category already exists
        try:
            Category.find_by_name(category.name)
            logger.debug(f"Category '{category.name}' already exists. Skipping insertion.")
            continue
        except ValueError:
            Category.create(
                category.name,
                description=category.description,
                color=category.color,
            )
    logger.info("default categories ensured.")


def strip_db():
    """
    removes all tables except for the notes, and removes processed note text so that everything can be reprocessed again
    """
    logger.debug("stripping database...")
    with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()
        # Drop all tables except for notes
        cursor.execute("DROP TABLE IF EXISTS actions")
        cursor.execute("DROP TABLE IF EXISTS todos")
        cursor.execute("DROP TABLE IF EXISTS commands")
        cursor.execute("DROP TABLE IF EXISTS annotations")
        cursor.execute("DROP TABLE IF EXISTS categories")
        cursor.execute("update notes set processed_note_text = ''")
        conn.commit()
    logger.info("database stripped.")
