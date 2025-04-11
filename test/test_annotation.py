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
    db.insert_default_categories()


def test_category_insertion(setup_database):
    # make sure the category were inserted correctly
    categories = db.Category.get_all()
    assert len(categories) > 0
    assert all(category.id is not None for category in categories)
    category_names = [category.name for category in categories]
    assert "action" in category_names
    assert "todo" in category_names
    assert "curiosity" in category_names
    assert "observation" in category_names
    assert "command" in category_names
    category_descriptions = [category.description for category in categories]
    assert not any(description is None for description in category_descriptions)


@pytest.fixture(scope="session")
def initial_note(setup_database):
    initial_note = db.Note.create(
        "I just woke up",
        timestamp="2025-4-05 10:00:00",
    )
    return initial_note


def test_create_note(initial_note):
    # create a test note to work with
    assert initial_note is not None
    # make sure the note was inserted correctly
    assert initial_note.id is not None
    assert initial_note.note_text == "I just woke up"
    assert initial_note.timestamp == "2025-4-05 10:00:00"


def test_process_note(initial_note):
    # try to annotate the note
    category = processor.categorize_note(initial_note)
    assert category is not None
    assert category.name == "action"
    

notes_categories = {
    "action": [
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
    "todo": [
        "I need to finish my project",
        "I will talk to the vendor",
        "The truck needs its oil changed",
        "I need to call my mom",
        "I need to work out today", 
        "I need to do laundry",
        "I need to clean the house"
    ],
    "curiosity": [
        "I wonder how many cities there are in the US",
        "Can I use asserts in a pytest fixture?",
        "I wonder how many people are in the world",
        "How do I do tests in golang?"
    ],
    "observation": [
        "I noticed there is a new restaurant in town",
        "The tomatoes are ripe",
        "Today is a sunny day",
        "10 clients crashed the server on a raspberry pi zero W",
        "The truck had its SRS light on today"
    ],
    "command": [
        "Change the note about waking up to an actiion",
        "Update the timestamp for finishing my workout to 1:30"
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
            "action": success_obj.copy(),
            "todo": success_obj.copy(),
            "curiosity": success_obj.copy(),
            "observation": success_obj.copy(),
            "command": success_obj.copy()
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
        assert success_rate["action"]["fail"] == 0
        assert success_rate["todo"]["fail"] == 0
        assert success_rate["curiosity"]["fail"] == 0
        assert success_rate["observation"]["fail"] == 0
        assert success_rate["command"]["fail"] == 0


def test_annotate_curiosity(mock_sqlite3_connect):
    # create a test note to work with
    initial_note = db.Note.create(
        "I wonder what ingredients are in homemade pasta",
        timestamp="2025-4-05 10:00:00",
    )
    category = db.Category.find_by_name("curiosity")
    assert category is not None
    assert category.name == "curiosity"
    # try to annotate the note
    annotation = processor.annotate_note(initial_note, category)
    assert annotation is not None
    assert annotation.note_id == initial_note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text is not None
    initial_note.refresh()
    assert initial_note.processed_note_text is not None


def test_annotate_action(mock_sqlite3_connect):
    # create a test note to work with
    initial_note = db.Note.create(
        "I am going to the gym",
        timestamp="2025-4-05 10:00:00",
    )
    category = db.Category.find_by_name("action")
    assert category is not None
    assert category.name == "action"
    # try to annotate the note
    annotation = processor.annotate_note(initial_note, category)
    assert annotation is not None
    assert annotation.note_id == initial_note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text is not None
    initial_note.refresh()
    assert initial_note.processed_note_text is not None


def test_annotate_todo(mock_sqlite3_connect):
    # create a test note to work with
    initial_note = db.Note.create(
        "I need to clean the pool filter tomorrow morning",
        timestamp="2025-4-05 10:00:00",
    )
    category = db.Category.find_by_name("todo")
    assert category is not None
    assert category.name == "todo"
    # try to annotate the note
    annotation = processor.annotate_note(initial_note, category)
    assert annotation is not None
    assert annotation.note_id == initial_note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text is not None
    initial_note.refresh()
    assert initial_note.processed_note_text is not None


def test_annotate_observation(mock_sqlite3_connect):
    # create a test note to work with
    initial_note = db.Note.create(
        "The tomatoes are ripe",
        timestamp="2025-4-05 10:00:00",
    )
    category = db.Category.find_by_name("observation")
    assert category is not None
    assert category.name == "observation"
    # try to annotate the note
    annotation = processor.annotate_note(initial_note, category)
    assert annotation is not None
    assert annotation.note_id == initial_note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text is not None
    initial_note.refresh()
    assert initial_note.processed_note_text is not None


def test_annotate_command(mock_sqlite3_connect):
    # create a test note to work with
    initial_note = db.Note.create(
        "Change the note about waking up to an action",
        timestamp="2025-4-05 10:00:00",
    )
    category = db.Category.find_by_name("command")
    assert category is not None
    assert category.name == "command"
    # try to annotate the note
    annotation = processor.annotate_note(initial_note, category)
    assert annotation is not None
    assert annotation.note_id == initial_note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text is not None
    initial_note.refresh()
    assert initial_note.processed_note_text is not None
