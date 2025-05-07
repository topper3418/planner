import pytest

from src import db, processor


def test_create_two_actions(refresh_database):
    note = db.Note.create(
        "I woke up 15 minutes sgo, and just finished cooking breakfast",
        timestamp="2025-05-03 08:00:00"
    )
    note_processor = processor.NoteProcessor(note)
    note_processor.process_note()
    # two actions should have been created]
    assert len(note.actions) == 2, f"two actions should have been created from this first note"


def test_create_two_actions_lighter(refresh_database): 
    note = db.Note.create(
        "I woke up 15 minutes sgo, and just finished cooking breakfast",
        timestamp="2025-05-03 08:00:00"
    )
    note_processor = processor.NoteProcessor(note)
    response = note_processor.client.responses.create(
        model="gpt-3.5-turbo",
        instructions=note_processor.annotation_system_prompt,
        input=note_processor.note.model_dump_json(),
        tools=note_processor.annotation_tools,
    )
    from pprint import pprint
    pprint(response)
