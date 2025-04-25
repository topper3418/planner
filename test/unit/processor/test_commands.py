import pytest

from src import db, processor


def bulk_upload_notes(note_list):
    for timestamp, note_text, category_name in note_list:
        note = db.Note.create(
            note_text,
            timestamp=timestamp,
        )
        category = db.Category.get_by_name(category_name)
        db.Annotation.create(
            note_id=note.id,
            category_id=category.id,
            annotation_text=note_text,
        )


@pytest.fixture(scope="session")
def create_notes_for_morning(setup_database):
    """
    creates a bunch of categorized notes for the morning
    """
    # reset the database
    db.teardown()
    db.ensure_tables()
    db.ensure_default_categories()
    notes = [
        ("2025-04-05 08:00:00", "I woke up", "observation"),
        ("2025-04-05 08:30:00", "I am going to the gym real quick", "action"),
        ("2025-04-05 09:00:00", "I need to clean the pool filter later today", "todo"),
        ("2025-04-05 09:30:00", "I need to call my mom", "todo"),
        ("2025-04-05 10:00:00", "I wonder how many people are in the world", "curiosity"),
        ("2025-04-05 10:30:00", "The tomatoes are ripe", "observation"),
        ("2025-04-05 11:00:00", "taking a break to eat lunch", "action"),
    ]
    bulk_upload_notes(notes)
    

@pytest.mark.parametrize(
    "note_text, expected_command, note_search",
    [
        ("Change the note about waking up to an action", "update_note_category", "I woke up"),
        ("That note about going to the gym, I actually meant to say garage", "update_note_text", "gym real quick"),
        ("I need you to do my homework for me", "no_match_found", "N/A")
    ],
    ids=[
        "update_note_category",
        "update_note_text",
        "no_match_found"
    ]
)
def test_create_commands(create_notes_for_morning, note_text, expected_command, note_search):
    # create a test note to work with
    initial_note = db.Note.create(note_text)
    category = db.Category.get_by_name("command")
    assert category is not None
    assert category.name == "command"
    # try to annotate the note
    annotation = processor.annotate_note(initial_note, category)
    assert annotation is not None
    assert annotation.note_id == initial_note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text is not None
    initial_note.refresh()
    assert initial_note.processed_note_text is not None
    # try to create the command
    command = processor.create_command(annotation)
    if note_search != "N/A":
        assert command is not None
        assert command.source_annotation == annotation
        assert command.command_text == expected_command
        assert command.value_before is not None
        assert command.desired_value is not None
        # find the note to make sure that the command points to the right note
        notes = db.Note.get_all(search=note_search)
        note = notes[-1] if notes else None
        assert note is not None  # this isn't the point of the test but good to know
        assert note.id == command.target_id
    else: 
        assert command is None


@pytest.fixture(scope="session")
def create_notes_for_afternoon(create_notes_for_morning):
    """
    creates a bunch of categorized notes for the afternoon
    """
    notes = [
        ("2025-04-05 12:00:00", "I am going to the store", "observation"),
        ("2025-04-05 12:30:00", "I need to finish my project", "todo"),
        ("2025-04-05 13:00:00", "I wonder how many cities there are in the US", "curiosity"),
        ("2025-04-05 13:30:00", "The truck needs its oil changed", "todo"),
        ("2025-04-05 14:00:00", "I need to do laundry", "todo"),
        ("2025-04-05 14:30:00", "I need to clean the house", "todo"),
        ("2025-04-05 15:00:00", "talked to the wife for a few minutes", "action"),
        ("2025-04-05 15:30:00", "I am going to spend an hour at the gym", "action"),
        ("2025-04-05 16:00:00", "I need to call my mom", "todo"),
        ("2025-04-05 16:30:00", "I am going to bed", "action"),
        ("2025-04-05 17:00:00", "I pushed my commit", "action"),
        ("2025-04-05 17:30:00", "I found and fixed the bug", "action"),
    ]
    bulk_upload_notes(notes)


@pytest.mark.parametrize(
    "note_text, expected_command, note_search",
    [
        ("Change the note about going to the store to an action", "update_note_category", "I am going to the store"),
        ("That note about finishing my project, change it because I actually meant to say I need to start my project", "update_note_text", "finish my project"),
        ("I need you to backfill everything I did today", "no_match_found", "N/A"),
        ("change the note about going to the gym, I actually meant I was going to the garage", "update_note_text", "I am going to spend an hour at the gym")
    ],
    ids=[
        "update_note_category2",
        "update_note_text2",
        "no_match_found2",
        "update_note_text3"
    ]
)
def test_create_commands_2(create_notes_for_afternoon, note_text, expected_command, note_search):
    # create a test note to work with
    initial_note = db.Note.create(note_text)
    category = db.Category.get_by_name("command")
    assert category is not None
    assert category.name == "command"
    # try to annotate the note
    annotation = processor.annotate_note(initial_note, category)
    assert annotation is not None
    assert annotation.note_id == initial_note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text is not None
    initial_note.refresh()
    assert initial_note.processed_note_text is not None
    # try to create the command
    command = processor.create_command(annotation)
    if note_search != "N/A":
        assert command is not None, (
            f"Command should not be None for note: {note_text}. "
            f"Expected {expected_command}"
        )
        assert command.source_annotation == annotation
        assert command.command_text == expected_command
        assert command.value_before is not None
        assert command.desired_value is not None
        # find the note to make sure that the command points to the right note
        notes = db.Note.get_all(search=note_search)
        note = notes[-1] if notes else None
        assert note is not None  # this isn't the point of the test but good to know
        assert note.id == command.target_id
    else: 
        assert command is None


def test_invalid_command(create_notes_for_afternoon):
    # create a test note to work with
    initial_note = db.Note.create("I need you to do my homework for me")
    category = db.Category.get_by_name("command")
    assert category is not None
    assert category.name == "command"
    # try to annotate the note
    annotation = processor.annotate_note(initial_note, category)
    assert annotation is not None
    assert annotation.note_id == initial_note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text is not None
    # try to create the command
    command = processor.create_command(annotation)
    assert command is None
    # see what happens to the note
    initial_note.refresh()
    assert initial_note.processed_note_text is not None
    assert initial_note.processing_error is not None
    # double check the note
    fetched_note = db.Note.get_by_id(initial_note.id)
    assert fetched_note is not None
    assert len(fetched_note.processing_error) > 0
