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


@pytest.fixture(scope="session")
def setup_database(mock_sqlite3_connect):
    # SETUP: ensure tables are created
    db.ensure_tables()

    # SETUP: insert the default category
    db.insert_default_categories()


def test_category_insertion(setup_database):
    # make sure the category were inserted correctly
    categories = db.Category.get_all()
    assert len(categories) > 0
    assert all(category.id is not None for category in categories)
    category_names = [category.name for category in categories]
    assert "Action" in category_names
    assert "Todo" in category_names
    assert "Curiosity" in category_names
    assert "Observation" in category_names
    category_descriptions = [category.description for category in categories]
    assert not any(description is None for description in category_descriptions)


@pytest.fixture(scope="session")
def initial_note(setup_database):
    initial_note = db.Note.create(
        "I just woke up",
        timestamp="2025-4-05 10:00:00",
        processed=False,
    )
    return initial_note


def test_create_note(initial_note):
    # create a test note to work with
    assert initial_note is not None
    # make sure the note was inserted correctly
    assert initial_note.id is not None
    assert initial_note.note_text == "I just woke up"
    assert initial_note.timestamp == "2025-4-05 10:00:00"
    assert initial_note.processed == False


def test_process_note(initial_note):
    # try to annotate the note
    category = processor.categorize_note(initial_note)
    assert category is not None
    assert category.name == "Action"
    

notes_categories = {
    "Action": [
        "I am finished with work for the day",
        "I pushed my commit",
        "I am going to bed",
        "I am taking a break",
        "I am starting on my garden project",
        "I found and fixed the bug",
        "I am going to the gym",
        "Starting on my project",
        "talked to the wife for a few minutes"
    ],
    "Todo": [
        "I need to finish my project",
        "I will talk to the vendor",
        "The truck needs its oil changed",
        "I need to call my mom",
        "I need to work out today", 
        "I need to do laundry",
        "I need to clean the house"
    ],
    "Curiosity": [
        "I wonder how many cities there are in the US",
        "Can I use asserts in a pytest fixture?",
        "I wonder how many people are in the world",
        "How do I do tests in golang?"
    ],
    "Observation": [
        "I noticed there is a new restaurant in town",
        "The tomatoes are ripe",
        "Today is a sunny day",
        "10 clients crashed the server on a raspberry pi zero W",
        "The truck had its SRS light on today"
    ],
    "Command": [
        ""
    ]
}

def test_process_notes():
    # create a test note to work with
    for category_name, notes in notes_categories.items():
        success_obj = {
            "success": 0,
            "fail": 0
        }
        success_rate = {
            "Action": success_obj.copy(),
            "Todo": success_obj.copy(),
            "Curiosity": success_obj.copy(),
            "Observation": success_obj.copy()
        }
        for note_text in notes:
            note = db.Note.create(note_text)
            category = processor.categorize_note(note)
            assert category is not None
            if category.name == category_name:
                success_rate[category_name]["success"] += 1
            else:
                print(f"Failed to categorize note: {note_text}. Expected {category_name}, got {category.name}")
                success_rate[category_name]["fail"] += 1
        assert success_rate["Action"]["fail"] == 0
        assert success_rate["Todo"]["fail"] == 0
        assert success_rate["Curiosity"]["fail"] == 0
        assert success_rate["Observation"]["fail"] == 0


