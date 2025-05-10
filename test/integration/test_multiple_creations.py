import pytest

from src import db, engine


@pytest.mark.parametrize(
    "note_text, expected_actions, expected_todos, expected_curiosities",
    [
        (
            "I woke up about 10 minutes ago and I just brushed my teeth",
            2,  # Expected number of actions
            0,  # Expected number of todos
            0   # Expected number of curiosities
        ),
        (
            "I just woke up and need to change the oil in the truck.",
            1,
            1,
            0
        ),
        (
            "I need to call my mom and pick up groceries.",
            0,
            2,
            0
        ),
        (
            "I just walked watered the garden and I remembered that I need to buy more basil seeds and I need to buy more trellises",
            1,
            2,
            0
        ),
        (
            "I just fihished working on the coding project for the day. I need to work on the security part of it tomorrow.",
            1,
            1,
            0
        ),
        (
            "I wonder what the weather will be like tomorrow. If it's nice, I might go for a walk.",
            0,
            1,
            1
        )
    ]
)
def test_create_multiple_items(
        refresh_database,
        note_text,
        expected_actions,
        expected_todos, 
        expected_curiosities
):
    # Create a note with multiple actions
    note = db.Note.create(note_text)
    engine.cycle()

    # Check that the correct number of actions were created
    actions = note.actions
    assert len(actions) == expected_actions

    # Check that the correct number of todos were created
    todos = note.todos
    assert len(todos) == expected_todos

    # Check that the correct number of curiosities were created
    curiosities = note.curiosities
    assert len(curiosities) == expected_curiosities
