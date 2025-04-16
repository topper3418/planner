import pytest
from datetime import datetime
from src import db, config


timestamp = datetime.strptime("2025-04-05 10:00:00", config.TIMESTAMP_FORMAT)

@pytest.fixture(scope="session")
def initial_note(setup_database):
    initial_note = db.Note.create(
        "I just woke up",
        timestamp=timestamp,
    )
    return initial_note


def test_create_note(initial_note):
    # create a test note to work with
    assert initial_note is not None
    # make sure the note was inserted correctly
    assert initial_note.id is not None
    assert initial_note.note_text == "I just woke up"
    assert initial_note.timestamp == timestamp
