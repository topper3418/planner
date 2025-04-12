import pytest
import sqlite3
from unittest.mock import patch

from src import db

@pytest.fixture(scope="session")
def mock_sqlite3_connect():
    # Create an in-memory database with shared cache that persists across tests
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    
    # Mock sqlite3.connect to return our in-memory connection
    with patch("sqlite3.connect") as mock_connect:
        mock_connect.return_value = conn
        yield conn
    
    # Cleanup after all tests are done
    conn.close()


@pytest.fixture(scope="session")
def setup_database(mock_sqlite3_connect):
    # SETUP: ensure tables are created
    db.ensure_tables()

    # SETUP: insert the default category
    db.ensure_default_categories()

