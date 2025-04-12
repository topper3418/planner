import pytest

from src import db, processor, utils


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
