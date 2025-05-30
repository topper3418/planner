# user configured settings will be stored in a SQLite database
import os
import sqlite3


def get_settings_connection():
    """
    Establishes a connection to the SQLite database for configuration.
    """
    connection = sqlite3.connect(os.path.join("data", "config.db"))
    return connection


def init_settings_db():
    """
    Initializes the settings database with a table for configuration values.
    """
    print("Initializing settings database...")
    connection = get_settings_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    connection.commit()
    connection.close()
    # ensure the notebook setting is initialized
    notebook = get_setting("notebook")
    if notebook is None:
        write_setting("notebook", "default")


def get_setting(key: str):
    """
    Retrieves a setting value by its key.
    """
    connection = get_settings_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None


def write_setting(key: str, value: str):
    """
    Writes a setting value by its key. If the key already exists, it updates the value.
    """
    connection = get_settings_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )
    connection.commit()
    connection.close()
