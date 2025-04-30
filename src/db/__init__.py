import logging
import sqlite3

from ..config import NOTES_DATABASE_FILEPATH

from .note import Note
from .annotation import Annotation
from .action import Action
from .todo import Todo
from .command import Command
from .curiosity import Curiosity

logger = logging.getLogger(__name__)


def ensure_tables():
    logger.debug("ensuring tables...")
    Note.ensure_table()
    Annotation.ensure_table()
    Action.ensure_table()
    Todo.ensure_table()
    Command.ensure_table()
    Curiosity.ensure_table()
    logger.info("tables ensured.")


def teardown():
    with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()
        # Drop all tables
        cursor.execute("DROP TABLE IF EXISTS actions")
        cursor.execute("DROP TABLE IF EXISTS todos")
        cursor.execute("DROP TABLE IF EXISTS commands")
        cursor.execute("DROP TABLE IF EXISTS annotations")
        cursor.execute("DROP TABLE IF EXISTS curiosities")
        cursor.execute("DROP TABLE IF EXISTS notes")
        conn.commit()

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
        cursor.execute("DROP TABLE IF EXISTS curiosities")
        cursor.execute("update notes set processed_note_text = ''")
        conn.commit()
    logger.info("database stripped.")
