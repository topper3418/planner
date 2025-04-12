import pytest
import sqlite3
import logging
from unittest.mock import patch

from src import db, processor, utils

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
        timestamp="2025-04-05 10:00:00",
    )
    return initial_note


def test_create_note(initial_note):
    # create a test note to work with
    assert initial_note is not None
    # make sure the note was inserted correctly
    assert initial_note.id is not None
    assert initial_note.note_text == "I just woke up"
    assert initial_note.timestamp == "2025-04-05 10:00:00"


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


def test_annotate_curiosity(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "I wonder what ingredients are in homemade pasta",
        timestamp="2025-04-05 10:00:00",
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


def test_annotate_action(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "I am going to the gym",
        timestamp="2025-04-05 10:00:00",
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


def test_annotate_todo(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "I need to clean the pool filter tomorrow morning",
        timestamp="2025-04-05 10:00:00",
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


def test_annotate_observation(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "The tomatoes are ripe",
        timestamp="2025-04-05 10:00:00",
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


def test_annotate_command(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "Change the note about waking up to an action",
        timestamp="2025-04-05 10:00:00",
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


def test_create_action(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "I am going to the gym",
        timestamp="2025-04-05 10:00:00",
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
    # try to create the action
    action = processor.create_action(annotation)
    assert action is not None
    assert action.source_annotation == annotation
    assert "gym" in action.action_text
    assert action.start_time == initial_note.timestamp


def test_create_recent_action(setup_database):
    """
    Tests the processor's ability to create an action the user just did
    """
    # create a test note to work with
    initial_note = db.Note.create(
        "I just spent 15 minutes cleaning the kitchen",
        timestamp="2025-04-05 10:00:00",
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
    # try to create the action
    action = processor.create_action(annotation)
    assert action is not None
    assert action.source_annotation == annotation
    assert "kitchen" in action.action_text
    start_time = utils.parse_time(action.start_time)
    assert action.end_time is not None
    end_time = utils.parse_time(action.end_time)
    now = utils.parse_time(initial_note.timestamp)
    assert start_time < now
    assert end_time > start_time
    diff = end_time - start_time
    assert diff.total_seconds() == 900  # 15 minutes


def test_create_immediate_action(setup_database):
    """
    Tests the processor's ability to create an action the user is about to do
    """
    # create a test note to work with
    initial_note = db.Note.create(
        "I am going to spend the next hour in the garden",
        timestamp="2025-04-05 10:00:00",
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
    # try to create the action
    action = processor.create_action(annotation)
    assert action is not None
    assert action.source_annotation == annotation
    assert "garden" in action.action_text
    assert action.start_time == initial_note.timestamp
    start_time = utils.parse_time(action.start_time)
    assert action.end_time is not None
    end_time = utils.parse_time(action.end_time)
    now = utils.parse_time(initial_note.timestamp)
    assert end_time > start_time
    assert end_time > now
    diff = end_time - start_time
    assert diff.total_seconds() == 3600  # 1 hour


def test_create_retroactive_action(setup_database):
    """
    Tests the processor's ability to create an action the user did in the past
    """
    # create a test note to work with
    initial_note = db.Note.create(
        "I spent 30 minutes cleaning the kitchen this morning",
        timestamp="2025-04-05 15:00:00",
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
    # try to create the action
    action = processor.create_action(annotation)
    assert action is not None
    assert action.source_annotation == annotation
    assert "kitchen" in action.action_text
    start_time = utils.parse_time(action.start_time)
    assert action.end_time is not None
    end_time = utils.parse_time(action.end_time)
    now = utils.parse_time(initial_note.timestamp)
    assert start_time < now
    assert end_time < now
    diff = end_time - start_time
    assert diff.total_seconds() == 1800  # 30 minutes


def test_create_retroactive_action_2(setup_database):
    """
    Tests the processor's ability to create an action the user did in the past
    """
    # create a test note to work with
    initial_note = db.Note.create(
        "I worked out for about an hour last night around 8",
        timestamp="2025-04-05 15:00:00",
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
    # try to create the action
    action = processor.create_action(annotation)
    assert action is not None
    assert action.source_annotation == annotation
    assert "work" in action.action_text.lower()
    assert "out" in action.action_text.lower()
    start_time = utils.parse_time(action.start_time)
    assert action.end_time is not None
    end_time = utils.parse_time(action.end_time)
    now = utils.parse_time(initial_note.timestamp)
    assert start_time < now
    assert end_time < now
    diff = end_time - start_time
    assert diff.total_seconds() == 3600  # 1 hour
    assert start_time.hour == 20  # 8 PM


def test_create_basic_todo(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "I need to clean the pool filter",
        timestamp="2025-04-05 10:00:00",
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
    # try to create the todo
    todo = processor.create_todo(annotation)
    assert todo is not None
    assert todo.source_annotation == annotation


def test_create_open_todo(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "I need to clean the pool filter tomorrow morning",
        timestamp="2025-04-05 10:00:00",
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
    # try to create the todo
    todo = processor.create_todo(annotation)
    assert todo is not None
    assert todo.source_annotation == annotation
    assert todo.target_start_time is not None
    assert todo.target_end_time is None
    assert todo.todo_text is not None
    start = utils.parse_time(todo.target_start_time)
    now = utils.parse_time(initial_note.timestamp)
    assert start.hour <= 12
    assert start.day == now.day + 1


def test_create_full_todo(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "I need to clean the pool filter tomorrow morning from 8 to 10",
        timestamp="2025-04-05 10:00:00",
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
    # try to create the todo
    todo = processor.create_todo(annotation)
    assert todo is not None
    assert todo.source_annotation == annotation
    assert todo.target_start_time is not None
    assert todo.target_end_time is not None
    assert todo.todo_text is not None
    start = utils.parse_time(todo.target_start_time)
    end = utils.parse_time(todo.target_end_time)
    now = utils.parse_time(initial_note.timestamp)
    assert start.hour == 8
    assert start.day == now.day + 1
    assert end.hour == 10
    assert end.day == now.day + 1


def bulk_upload_notes(note_list):
    for timestamp, note_text, category_name in note_list:
        note = db.Note.create(
            note_text,
            timestamp=timestamp,
        )
        category = db.Category.find_by_name(category_name)
        db.Annotation.create(
            note_id=note.id,
            category_id=category.id,
            annotation_text=note_text,
        )


@pytest.fixture(scope="session")
def create_notes_for_morning(setup_database):
    """
    creates a bunch of categorized notes for the morning
    """
    notes = [
        ("2025-04-05 08:00:00", "I woke up", "observation"),
        ("2025-04-05 08:30:00", "I am going to the gym real quick", "action"),
        ("2025-04-05 09:00:00", "I need to clean the pool filter later today", "todo"),
        ("2025-04-05 09:30:00", "I need to call my mom", "todo"),
        ("2025-04-05 10:00:00", "I wonder how many people are in the world", "curiosity"),
        ("2025-04-05 10:30:00", "The tomatoes are ripe", "observation"),
        ("2025-04-05 11:00:00", "taking a break to eat lunch", "action"),
    ]
    bulk_upload_notes(notes)
    


def test_create_commands(create_notes_for_morning):
    # create a list of tuples with the note text and expected command text
    test_samples = [
        ("Change the note about waking up to an action", "update_note_category", "I woke up"),
        ("That note about going to the gym, I actually meant to say garage", "update_note_text", "gym real quick"),
        ("I need you to do my homework for me", "no_match_found", "N/A")
    ]
    for note_text, expected_command, note_search in test_samples:
        # create a test note to work with
        initial_note = db.Note.create(note_text)
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
        # try to create the command
        command = processor.create_command(annotation)
        if note_search != "N/A":
            assert command is not None
            assert command.source_annotation == annotation
            assert command.command_text == expected_command
            assert command.value_before is not None
            assert command.desired_value is not None
            # find the note to make sure that the command points to the right note
            notes = db.Note.read(search=note_search)
            note = notes[-1] if notes else None
            assert note is not None  # this isn't the point of the test but good to know
            assert note.id == command.target_id
        else: 
            assert command is None


@pytest.fixture(scope="session")
def create_notes_for_afternoon(create_notes_for_morning):
    """
    creates a bunch of categorized notes for the afternoon
    """
    notes = [
        ("2025-04-05 12:00:00", "I am going to the store", "observation"),
        ("2025-04-05 12:30:00", "I need to finish my project", "todo"),
        ("2025-04-05 13:00:00", "I wonder how many cities there are in the US", "curiosity"),
        ("2025-04-05 13:30:00", "The truck needs its oil changed", "todo"),
        ("2025-04-05 14:00:00", "I need to do laundry", "todo"),
        ("2025-04-05 14:30:00", "I need to clean the house", "todo"),
        ("2025-04-05 15:00:00", "talked to the wife for a few minutes", "action"),
        ("2025-04-05 15:30:00", "I am going to spend an hour at the gym", "action"),
        ("2025-04-05 16:00:00", "I need to call my mom", "todo"),
        ("2025-04-05 16:30:00", "I am going to bed", "action"),
        ("2025-04-05 17:00:00", "I pushed my commit", "action"),
        ("2025-04-05 17:30:00", "I found and fixed the bug", "action"),
    ]
    bulk_upload_notes(notes)


def test_create_commands_2(create_notes_for_afternoon):
    # create a list of tuples with the note text and expected command text
    test_samples = [
        ("Change the note about going to the store to an action", "update_note_category", "I am going to the store"),
        ("That note about finishing my project, I actually meant to say I need to start my project", "update_note_text", "finish my project"),
        ("I need you to backfill everything I did today", "no_match_found", "N/A"),
        ("earlier today, when I said I was going to the gym, I actually meant I was going to the garage", "update_note_text", "I am going to spend an hour at the gym")
    ]
    for note_text, expected_command, note_search in test_samples:
        # create a test note to work with
        initial_note = db.Note.create(note_text)
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
        # try to create the command
        command = processor.create_command(annotation)
        if note_search != "N/A":
            assert command is not None
            assert command.source_annotation == annotation
            assert command.command_text == expected_command
            assert command.value_before is not None
            assert command.desired_value is not None
            # find the note to make sure that the command points to the right note
            notes = db.Note.read(search=note_search)
            note = notes[-1] if notes else None
            assert note is not None  # this isn't the point of the test but good to know
            assert note.id == command.target_id
        else: 
            assert command is None









