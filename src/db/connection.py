import sqlite3
from ..config import NOTES_DATABASE_FILEPATH


def get_connection(connection_path: str = NOTES_DATABASE_FILEPATH):
    """
    Establishes a connection to the SQLite database.
    """
    connection = sqlite3.connect(connection_path)
    return connection


