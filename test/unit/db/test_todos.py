import pytest
from datetime import datetime
from src import db, config, utils
import logging
from pprint import pformat

logger = logging.getLogger(__name__)


@pytest.fixture
def test_todo(setup_database):
    note = db.Note.create(
        "Test note for todo",
        timestamp="2023-04-12 12:00:00",
    )
    todo = db.Todo.create(
        todo_text="Test todo",
        source_note_id=note.id,
        target_start_time="2023-04-12 13:00:00",
        target_end_time="2023-04-12 14:00:00",
    )
    return note, todo


def test_create_todo(test_todo):
    note, todo = test_todo
    assert todo is not None
    assert todo.id is not None
    assert todo.todo_text == "Test todo"
    assert todo.source_note_id == note.id
    assert todo.target_start_time == utils.parse_time(
        "2023-04-12 13:00:00"
    )
    assert todo.target_end_time == utils.parse_time("2023-04-12 14:00:00")
    assert not todo.complete
    assert not todo.cancelled
    # Test source_note property
    assert todo.source_note is not None
    assert todo.source_note.id == note.id
    assert todo.source_note.note_text == "Test note for todo"


def test_todo_save(test_todo):
    note, todo = test_todo
    # Update todo fields
    todo.todo_text = "Updated todo"
    todo.complete = True
    todo.target_start_time = utils.parse_time("2023-04-12 15:00:00")
    todo.save()
    todo.refresh()
    # Verify updates
    assert todo.todo_text == "Updated todo"
    assert todo.complete
    assert todo.target_start_time == utils.parse_time(
        "2023-04-12 15:00:00"
    )
    # Double-check with fresh fetch
    todo_doublecheck = db.Todo.get_by_id(todo.id)
    assert todo_doublecheck is not None
    assert todo_doublecheck.todo_text == "Updated todo"
    assert todo_doublecheck.complete
    assert todo_doublecheck.target_start_time == utils.parse_time(
        "2023-04-12 15:00:00"
    )


def test_fetch_todo(test_todo):
    note, todo = test_todo
    assert todo is not None
    # Create additional todos
    note2 = db.Note.create(
        "Second test note",
        timestamp="2023-04-12 13:00:00",
    )
    todo2 = db.Todo.create(
        todo_text="Second test todo",
        source_note_id=note2.id,
        target_start_time="2023-04-12 14:00:00",
    )
    note3 = db.Note.create(
        "Third test note",
        timestamp="2023-04-12 14:00:00",
    )
    todo3 = db.Todo.create(
        todo_text="Third test todo",
        source_note_id=note3.id,
        target_start_time="2023-04-12 15:00:00",
    )
    # Fetch all todos
    all_todos = db.Todo.get_all()
    assert len(all_todos) >= 3
    assert all(todo.id is not None for todo in all_todos)
    assert all(todo.todo_text is not None for todo in all_todos)
    # Fetch by ID
    fetched_todo = db.Todo.get_by_id(todo.id)
    assert fetched_todo is not None
    assert fetched_todo.id == todo.id
    assert fetched_todo.todo_text == todo.todo_text
    assert fetched_todo.source_note_id == todo.source_note_id
    # Search by text
    searched_todos = db.Todo.get_all(search="Second test")
    assert len(searched_todos) > 0
    assert all("Second test" in todo.todo_text for todo in searched_todos)
    # Fetch by time bounds
    timed_todos = db.Todo.get_all(
        after="2023-04-12 12:00:00",
        before="2023-04-12 15:00:00",
    )
    assert len(timed_todos) > 0
    assert all(
        todo.target_start_time >= utils.parse_time("2023-04-12 12:00:00")
        or todo.target_end_time >= utils.parse_time("2023-04-12 12:00:00")
        or todo.source_note.timestamp
        >= utils.parse_time("2023-04-12 12:00:00")
        for todo in timed_todos
    )
    assert all(
        todo.target_start_time <= utils.parse_time("2023-04-12 15:00:00")
        or todo.target_end_time <= utils.parse_time("2023-04-12 15:00:00")
        or todo.source_note.timestamp
        <= utils.parse_time("2023-04-12 15:00:00")
        for todo in timed_todos
    )


def test_todo_delete(test_todo):
    note, todo = test_todo
    # Create an action linked to the todo
    action = db.Action.create(
        action_text="Complete todo",
        timestamp=note.timestamp,
        source_note_id=note.id,
        todo_id=todo.id,
        mark_complete=True,
    )
    todo.complete = True
    todo.save()
    # Verify setup
    assert todo.complete
    assert action.todo_id == todo.id
    assert action.mark_complete
    # Delete todo
    todo.delete()
    # Verify deletion
    deleted_todo = db.Todo.get_by_id(todo.id)
    assert deleted_todo is None
    # Verify action still exists but is no longer linked
    action.refresh()
    assert action is not None
    assert action.todo_id == todo.id  # Action retains todo_id
    assert action.mark_complete  # Action retains completion status


def test_todo_incomplete_and_cancelled(test_todo):
    note, todo = test_todo
    # Mark todo as cancelled
    todo.cancelled = True
    todo.save()
    todo.refresh()
    assert todo.cancelled
    # Fetch incomplete todos
    incomplete_todos = db.Todo.get_incomplete()
    assert todo not in incomplete_todos
    # Fetch cancelled todos
    cancelled_todos = db.Todo.get_cancelled()
    assert todo in cancelled_todos
    # Test active todos
    active_todos = db.Todo.get_all(active=True)
    assert todo not in active_todos


def test_todo_parent_child(test_todo):
    note, todo = test_todo
    # Create a child todo
    child_todo = db.Todo.create(
        todo_text="Child todo",
        source_note_id=note.id,
        parent_id=todo.id,
    )
    # Verify parent-child relationship
    assert child_todo.parent_id == todo.id
    assert child_todo.parent == todo
    children = todo.children
    assert len(children) > 0
    assert any(child.id == child_todo.id for child in children)
