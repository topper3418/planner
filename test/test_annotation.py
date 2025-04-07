import pytest
import sqlite3
import logging
from unittest.mock import patch

from src import db, processor

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def mock_sqlite3_connect():
    # Create an in-memory database with shared cache that persists across tests
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    logger.info('created in-memory database')
    
    # Mock sqlite3.connect to return our in-memory connection
    with patch("sqlite3.connect") as mock_connect:
        mock_connect.return_value = conn
        yield conn
    
    # Cleanup after all tests are done
    conn.close()
    logger.info('successfully closed in-memory database')

def test_annotation(mock_sqlite3_connect):
    # SETUP: ensure tables are created
    db.ensure_tables()

    # SETUP: insert the default topic
    db.insert_default_topics()
    # make sure the topic were inserted correctly
    topics = db.Topic.get_all()
    assert len(topics) > 0
    assert all(topic.id is not None for topic in topics)
    topic_names = [topic.name for topic in topics]
    assert "Action" in topic_names
    assert "Todo" in topic_names
    assert "Curiosity" in topic_names
    assert "Discovery" in topic_names
    topic_descriptions = [topic.description for topic in topics]
    assert not any(description is None for description in topic_descriptions)

    # create a test note to work with
    initial_note = db.Note.create(
        "I just woke up",
        timestamp="2025-4-05 10:00:00",
        processed=False,
    )
    assert initial_note is not None
    # make sure the note was inserted correctly
    assert initial_note.id is not None
    assert initial_note.note_text == "I just woke up"
    assert initial_note.timestamp == "2025-4-05 10:00:00"
    assert initial_note.processed == False

    # try to annotate the note
    note = processor.process_unprocessed_note()
    assert note is not None
    assert note.processed == True
    
    # Here's where you can call your function to test
    # For example: result = your_function(note_id)
    # Then add assertions about the result
    # YOUR_FUNCTION_CALL_HERE
