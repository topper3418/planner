import sqlite3
import os
from ..settings import get_setting


def get_connection(notebook: str | None = None) -> sqlite3.Connection:
    """
    Establishes a connection to the SQLite database.
    """
    if notebook is None:
        notebook = get_setting("notebook") or "default"
    connection_path = os.path.join("data", "notebooks", f"{notebook}.db")
    connection = sqlite3.connect(connection_path)
    return connection
