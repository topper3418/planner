import pytest
from datetime import datetime
import logging
from pprint import pformat

from src import db, config, bulk_upload_notes_list, utils
from sample.a_days_notes import notes as sample_note_list

logger = logging.getLogger(__name__)


def test_create_note(setup_database):
    timestamp = datetime.strptime(
        "2025-04-05 10:00:00", config.TIMESTAMP_FORMAT
    )
    initial_note = db.Note.create(
        "I just woke up",
        timestamp=timestamp,
    )
    # create a test note to work with
    assert initial_note is not None
    # make sure the note was inserted correctly
    assert initial_note.id is not None
    assert initial_note.note_text == "I just woke up"
    assert initial_note.timestamp == timestamp


@pytest.fixture
def sample_notes(setup_database):
    return bulk_upload_notes_list(sample_note_list)


def test_save_note(sample_notes):
    # Test saving a new note
    found_notes = db.Note.get_all(search="Woke up and")
    assert len(found_notes) > 0
    wake_up_note = found_notes[0]
    assert wake_up_note.note_text == "Woke up and rolled out of bed."
    wake_up_note.note_text = "I just woke up"
    wake_up_note.save()
    wake_up_note.refresh()
    assert wake_up_note.note_text == "I just woke up"
    # make sure the reload worked with a new fetch
    wake_up_note_doublecheck = db.Note.get_by_id(wake_up_note.id)
    assert wake_up_note_doublecheck is not None
    assert wake_up_note_doublecheck.note_text == "I just woke up"
    # make sure processing errors can be saved
    wake_up_note.processing_error = "Test error"
    wake_up_note.save()
    wake_up_note.refresh()
    assert wake_up_note.processing_error == "Test error"
    # make sure processed can be saved
    wake_up_note.processed = True
    wake_up_note.save()
    wake_up_note.refresh()
    assert wake_up_note.processed
    # last check
    note_fetched = db.Note.get_by_id(wake_up_note.id)
    assert note_fetched is not None
    assert note_fetched.note_text == "I just woke up"
    assert note_fetched.processing_error == "Test error"


def test_fetch_bounds(sample_notes):
    start_time = utils.parse_time("2023-04-12 12:00:00")
    end_time = utils.parse_time("2023-04-12 20:00:00")
    found_notes = db.Note.get_all(after=start_time, before=end_time)
    assert len(found_notes) > 0
    assert all(note.timestamp >= start_time for note in found_notes)
    assert all(note.timestamp <= end_time for note in found_notes)


def test_offset_and_limit(sample_notes):
    found_notes = db.Note.get_all(offset=0, limit=5)
    logger.info(f"Found {len(found_notes)} notes\n{pformat(found_notes)}")
    assert len(found_notes) == 5
    assert all(note.id is not None for note in found_notes)
    assert all(note.note_text is not None for note in found_notes)
    assert all(note.timestamp is not None for note in found_notes)
    first_max_id = max(note.id for note in found_notes)
    # test offset
    found_notes = db.Note.get_all(offset=5, limit=5)
    logger.info(f"Found {len(found_notes)} notes\n{pformat(found_notes)}")
    assert len(found_notes) == 5
    assert all(note.id is not None for note in found_notes)
    assert all(note.note_text is not None for note in found_notes)
    assert all(note.timestamp is not None for note in found_notes)
    assert all(note.id < first_max_id for note in found_notes)


def test_unprocessed_note_search(sample_notes):
    first_unprocessed_note = db.Note.get_next_unprocessed_note()
    assert first_unprocessed_note is not None
    assert first_unprocessed_note.processed_note_text == ""
    assert first_unprocessed_note.note_text is not None
    first_unprocessed_note.processed = True
    first_unprocessed_note.save()
    second_unprocessed_note = db.Note.get_next_unprocessed_note()
    assert second_unprocessed_note is not None
    assert second_unprocessed_note.processed_note_text == ""
    assert second_unprocessed_note.note_text is not None
    assert second_unprocessed_note.id != first_unprocessed_note.id
