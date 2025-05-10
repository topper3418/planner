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
    db.init_db()


@pytest.fixture
def refresh_database(setup_database):
    db.teardown()
    db.init_db()


@pytest.fixture
def sample_todos(refresh_database):
    first_note = db.Note.create("Placeholder")
    first_annotation = db.Annotation.create(
        note_id=first_note.id,
        annotation_text="This is a test annotation",
    )
    ann_id = first_annotation.id
    todos = [
        db.Todo.create(
            todo_text="finish my coding project",
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="talk to the vendor",
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="change the oil in the truck",
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="call my mom",
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="work out today",
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="do laundry",
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="clean the house",
            source_note_id=ann_id,
        ),
    ]
    return todos
