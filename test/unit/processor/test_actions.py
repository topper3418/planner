import pytest
from datetime import datetime

from src import db, processor, config


def test_create_action(setup_database):
    # create a test note to work with
    timestamp = datetime.strptime("2025-04-05 10:00:00", config.TIMESTAMP_FORMAT)
    initial_note = db.Note.create(
        "I am going to the gym",
        timestamp=timestamp,
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
    timestamp = datetime.strptime("2025-04-05 10:00:00", config.TIMESTAMP_FORMAT)
    initial_note = db.Note.create(
        "I just spent 15 minutes cleaning the kitchen",
        timestamp=timestamp,
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
    assert action.start_time == initial_note.timestamp
    assert "15 minutes" in action.action_text


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
    assert "1 hour" in action.action_text


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
    assert "30 minutes" in action.action_text
    assert action.start_time.hour < 12


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
    start_time = action.start_time
    assert start_time.day == initial_note.timestamp.day - 1
    assert "1 hour" in action.action_text
    assert start_time.hour == 20  # 8 PM
