import pytest

from src import db


def test_create_command(setup_database):
    # create a test command to work with
    note = db.Note.create(
        "I just woke up",
        timestamp="2023-04-12 12:00:00",
    )
    category = db.Category.find_by_name("action")
    annotation = db.Annotation.create(
        note.id,
        category.id,
        "Test annotation",
    )
    command = db.Command.create(
        "Test command",
        "value_before",
        "desired_value",
        annotation.id,
        5,
    )
    assert command is not None
    assert command.id is not None
    assert command.command_text == "Test command"
    assert command.value_before == "value_before"
    assert command.desired_value == "desired_value"
    assert command.source_annotation_id == 1
    assert command.target_id == 5
