import pytest

from src import db, processor


def test_annotate_curiosity(setup_database):
    # create a test note to work with
    initial_note = db.Note.create(
        "I wonder what ingredients are in homemade pasta",
        timestamp="2025-04-05 10:00:00",
    )
    category = db.Category.get_by_name("curiosity")
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
    category = db.Category.get_by_name("action")
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
    category = db.Category.get_by_name("todo")
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
    category = db.Category.get_by_name("observation")
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
    category = db.Category.get_by_name("command")
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

