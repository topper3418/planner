import pytest

from src import db, engine, processor
from src.processor.create_command import get_target_note_id


def test_target_first_note(setup_database):
    # start the db fresh
    db.teardown()
    db.ensure_tables()
    db.ensure_default_categories()
    # Create a test note
    test_note = db.Note.create(
        "I just woke up",
        timestamp="2023-04-12 06:00:00"
    )
    # cycle the engine to categorize the first note
    engine.cycle()
    # Get the first note from the sample notes
    first_note = db.Note.get_all(search="I just woke up")[0]
    assert first_note is not None
    first_annotation = db.Annotation.get_by_source_note_id(first_note.id)
    assert first_annotation is not None
    assert first_annotation.category.name == "action"
    # Create a command to recategorize the note
    command_note = db.Note.create(
        f"recategorize note {first_note.id} to an observation",
        timestamp="2023-04-12 06:15:00"
    )
    # create an annotation for the command note
    command_annotation = db.Annotation.create(
        note_id=command_note.id,
        category_id=db.Category.get_by_name("command").id,
        annotation_text="The user wants to recategorize note with id 1 to the category 'observation'.",
    )
    # make sure the command note is categorized as a command
    command_annotation = db.Annotation.get_by_source_note_id(command_note.id)
    assert command_annotation is not None
    assert command_annotation.category.name == "command"
    # have it find the target note
    target_id = get_target_note_id(command_annotation)
    assert target_id == first_note.id
