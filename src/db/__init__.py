from datetime import datetime
import logging
import sqlite3

from ..errors import MigrationError
from ..config import NOTES_DATABASE_FILEPATH
from ..util import get_git_version

from .version import Version
from .note import Note
from .action import Action
from .todo import Todo
from .tool_call import ToolCall
from .curiosity import Curiosity

logger = logging.getLogger(__name__)

DB_VERSION = "0.1.0"


def init_db():
    logger.debug("ensuring tables...")

    version = get_git_version()
    Version.init(
        db_version=DB_VERSION,
        commit_hash=version.commit,
        branch=version.branch,
    )
    Note.ensure_table()
    Action.ensure_table()
    Todo.ensure_table()
    ToolCall.ensure_table()
    Curiosity.ensure_table()
    logger.info("tables ensured.")


def teardown():
    with sqlite3.connect(NOTES_DATABASE_FILEPATH) as conn:
        cursor = conn.cursor()
        # Drop all tables
        cursor.execute("DROP TABLE IF EXISTS actions")
        cursor.execute("DROP TABLE IF EXISTS todos")
        cursor.execute("DROP TABLE IF EXISTS tool_calls")
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
        cursor.execute("DROP TABLE IF EXISTS tool_calls")
        cursor.execute("DROP TABLE IF EXISTS curiosities")
        cursor.execute(
            "update notes set processed_note_text = '', processing_error = '', processed = 0"
        )
        conn.commit()
    logger.info("database stripped.")


def backup_db():
    """
    creates a backup of the database by copying it to a new file with a timestamp
    """
    import shutil

    logger.debug("backing up database...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{NOTES_DATABASE_FILEPATH}_{timestamp}.bak"
    shutil.copy(NOTES_DATABASE_FILEPATH, backup_file)


def migrate():
    """
    migrates the database to the current version
    """
    try:
        Version.migrate(DB_VERSION)
    except FileNotFoundError as fe:
        logger.error(f"migration file not found: {fe}")
        raise
    except MigrationError as me:
        logger.error(f"migration failed: {me}")
        raise
    except Exception as e:
        logger.error(f"migration failed due to unexpected error: {e}")
        raise
