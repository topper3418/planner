import pytest

from src import db, engine, processor



@pytest.fixture
def initial_note():
    # ensure clean test environment
    db.teardown()
    db.ensure_tables()
    db.ensure_default_categories()
    # Create a test note
    note = db.Note.create(
        "I just woke up",
        timestamp="2023-04-12 12:00:00",
    )
    return note

def test_recategorize_from_action(initial_note):
    # cycle the engine to categorize the note
    engine.cycle()
    # get the annotation for the note
    annotation = db.Annotation.get_by_note_id(initial_note.id)
    assert annotation is not None
    # get the action for the annotation
    action = db.Action.find_by_annotation_id(annotation.id)
    assert action is not None
    # simulate a cycle to remove the action and change the category
    # create a command to recategorize the note
    command_note = db.Note.create(
        f"recategorize note {initial_note.id} to an observation",
    )
    command_category = db.Category.find_by_name("command")
    annotation = db.Annotation.create(
        note_id=command_note.id,
        category_id=command_category.id,
        annotation_text="recategorize note",
    )
    command= db.Command.create(
        command_text="update_note_category",
        target_id=initial_note.id,
        desired_value="observation",
        value_before="action",
        source_annotation_id=initial_note.id,
    )
    processor.route_command(command)
    # Check that the note was recategorized
    new_annotation = db.Annotation.get_by_note_id(initial_note.id)
    assert new_annotation is not None
    assert new_annotation.category.name == "observation"
    # Check that the original action was deleted
    old_action = db.Action.get_by_id(action.id)
    assert old_action is None



