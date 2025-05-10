import pytest

from src import db


@pytest.fixture
def test_action(setup_database):
    note = db.Note.create(
        "I just woke up",
        timestamp="2023-04-12 12:00:00",
    )
    action = db.Action.create(
        "Test action",
        timestamp=note.timestamp,
        source_note_id=note.id,
    )
    return note, action


def test_create_action(test_action):
    note, action = test_action
    # create a test command to work with
    assert action is not None
    assert action.id is not None
    assert action.action_text == "Test action"
    assert action.timestamp == note.timestamp
    assert action.source_note_id == note.id
    # test the action properties
    assert action.source_note is not None
    assert action.source_note.id == note.id
    assert action.source_note.note_text == "I just woke up"


def test_action_save(test_action):
    note, action = test_action
    # update the action
    action.action_text = "Updated action"
    action.save()
    action.refresh()
    # make sure the update worked
    assert action.action_text == "Updated action"
    # make sure the reload worked with a new fetch
    action_doublecheck = db.Action.get_by_id(action.id)
    assert action_doublecheck is not None
    assert action_doublecheck.action_text == "Updated action"


def test_fetch_action(test_action):
    note, action = test_action
    # add a couple more notes, annotations, and actions
    note2 = db.Note.create(
        "I just woke up again",
        timestamp="2023-04-12 13:00:00",
    )
    action2 = db.Action.create(
        "Test action 2",
        timestamp=note2.timestamp,
        source_note_id=note2.id,
    )
    # make one more set
    note3 = db.Note.create(
        "I just woke up again and again",
        timestamp="2023-04-12 14:00:00",
    )
    action3 = db.Action.create(
        "Test action 3",
        timestamp=note3.timestamp,
        source_note_id=note3.id,
    )
    # fetch all actions
    all_actions = db.Action.get_all()
    assert len(all_actions) > 0
    assert all(action.id is not None for action in all_actions)
    assert all(action.action_text is not None for action in all_actions)
    # fetch the action by ID
    fetched_action = db.Action.get_by_id(action.id)
    assert fetched_action is not None
    assert fetched_action.id == action.id
    assert fetched_action.action_text == action.action_text
    assert fetched_action.timestamp == action.timestamp
    assert fetched_action.source_note_id == action.source_note_id
    # search an action by text
    searched_actions = db.Action.get_all(search="Test action 2")
    assert len(searched_actions) > 0
    assert all(action.id is not None for action in searched_actions)
    assert all(
        "Test action 2" in action.action_text
        for action in searched_actions
    )
    # fetch actions by start and end time
    timed_actions = db.Action.get_all(
        after=note.timestamp,
        before=note3.timestamp,
    )
    assert len(timed_actions) > 0
    assert all(
        action.timestamp >= note.timestamp for action in timed_actions
    )
    assert all(
        action.timestamp <= note3.timestamp for action in timed_actions
    )


def test_action_delete(test_action):
    note, action = test_action
    # create a todo to link the command with
    todo = db.Todo.create(
        "Test todo",
        target_end_time=note.timestamp,
        source_note_id=note.id,
    )
    action.todo_id = todo.id
    action.mark_complete = True
    todo.complete = True
    todo.save()
    action.save()
    # make sure the action is marked complete
    assert action.mark_complete
    assert action.todo_id == todo.id
    # make sure the todo is marked complete
    assert todo.complete
    # make sure the action is linked to the todo
    assert action.todo_id == todo.id
    # delete the action
    action.delete()
    # make sure the action is deleted
    deleted_action = db.Action.get_by_id(action.id)
    assert deleted_action is None
    # make sure the todo is marked incomplete
    todo.refresh()
    assert not todo.complete
