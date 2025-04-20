import pytest
from pprint import pformat, pprint

from src import db, config, engine

def test_recategorize_by_id():
    # create a test note, which should be an action
    test_note = db.Note.create(
        "I just woke up",
        timestamp="2023-04-12 06:00:00"
    )
    engine.cycle()
    annotation = db.Annotation.get_by_note_id(test_note.id)
    assert annotation is not None
    action = db.Action.find_by_annotation_id(annotation.id)
    assert action is not None
    assert annotation is not None
    assert annotation.category.name == "action"
    # create a test command to recategorize the note
    command_note = db.Note.create(
        f"recategorize note {test_note.id} to an observation",
    )
    engine.cycle()
    command_annotation = db.Annotation.get_by_note_id(command_note.id)
    assert command_annotation is not None
    assert command_annotation.category.name == "command"
    # make sure the note got recategorized
    new_annotation = db.Annotation.get_by_note_id(test_note.id)
    assert new_annotation is not None
    assert new_annotation.category.name == "observation"
    # make sure the original action was deleted
    old_action = db.Action.get_by_id(action.id)
    assert old_action is None






