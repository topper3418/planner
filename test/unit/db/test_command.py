import pytest

from src import db


@pytest.fixture
def first_command(setup_database):
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
    return note, category, annotation, command


def test_create_command(first_command):
    note, category, annotation, command = first_command
    assert command is not None
    assert command.id is not None
    assert command.command_text == "Test command"
    assert command.value_before == "value_before"
    assert command.desired_value == "desired_value"
    assert command.source_annotation_id == annotation.id
    assert command.target_id == 5


def test_get_command_by_id(first_command):
    note, category, annotation, command = first_command
    retrieved_command = db.Command.get_by_id(command.id)
    assert retrieved_command is not None
    assert retrieved_command.id == command.id
    assert retrieved_command.command_text == command.command_text
    assert retrieved_command.value_before == command.value_before
    assert retrieved_command.desired_value == command.desired_value
    assert retrieved_command.source_annotation_id == command.source_annotation_id
    assert retrieved_command.target_id == command.target_id


def test_update_and_refresh_command(first_command):
    note, category, annotation, command = first_command
    command.command_text = "Updated command"
    command.value_before = "new_value_before"
    command.desired_value = "new_desired_value"
    command.target_id = 10
    command.save()
    # Refresh the command to get the updated values
    command.refresh()
    assert command.command_text == "Updated command"
    assert command.value_before == "new_value_before"
    assert command.desired_value == "new_desired_value"
    assert command.target_id == 10
    # test getting it by id just to be sure
    retrieved_command = db.Command.get_by_id(command.id)
    assert retrieved_command is not None
    assert retrieved_command.command_text == command.command_text
    assert retrieved_command.value_before == command.value_before
    assert retrieved_command.desired_value == command.desired_value
    assert retrieved_command.target_id == command.target_id

