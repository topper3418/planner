import pytest

from src import db, processor


notes_sample = [
    ("2023-04-12 06:00:00", "Woke up and rolled out of bed."),
    ("2023-04-12 06:03:00", "Heard a strange noise outside, not sure what it was."),
    ("2023-04-12 06:07:00", "I need to to check the weather before heading out."),
    ("2023-04-12 06:10:00", "I just checked, the sky shows hints of blue amid morning clouds."),
    ("2023-04-12 06:12:00", "Change that note about when I checked the weather to an action."),
    ("2023-04-12 06:15:00", "Made a quick cup of coffee."),
    ("2023-04-12 06:20:00", "Wonder why the coffee aroma is extra strong today."),
    ("2023-04-12 06:22:00", "I need to write a note about the coffee strength."),
    ("2023-04-12 06:25:00", "Grab a snack on the way out."),
    ("2023-04-12 06:30:00", "The hallway light flickers briefly."),
    ("2023-04-12 06:35:00", "Left the house in a slight hurry, keys in hand."),
    ("2023-04-12 06:40:00", "Puzzled by a misplaced item I can’t recall setting down."),
    ("2023-04-12 07:00:00", "Plan to call the bank about a recent issue."),
    ("2023-04-12 07:05:00", "The street outside is unusually quiet this morning."),
    ("2023-04-12 07:10:00", "Picked up the newspaper from the doorstep."),
    ("2023-04-12 07:20:00", "Remind myself to follow up on an important email."),
    ("2023-04-12 07:30:00", "Wonder why my phone buzzes at odd intervals."),
    ("2023-04-12 07:40:00", "A passing car made a peculiar sound near the curb."),
    ("2023-04-12 07:50:00", "Grabbed a quick breakfast on the go."),
    ("2023-04-12 08:00:00", "Check the message about tomorrow's meeting later."),
    ("2023-04-12 08:10:00", "Noticed an odd pattern in the early morning light."),
    ("2023-04-12 08:20:00", "Traffic on the main road is starting to build."),
    ("2023-04-12 08:30:00", "Joined a brief team check-in on the move."),
    ("2023-04-12 08:40:00", "Buy a new charger; mine’s been acting up."),
    ("2023-04-12 08:50:00", "Wonder if that soft sound was the bus arriving or just the wind."),
    ("2023-04-12 09:00:00", "Spotted a cluster of birds resting on the power lines."),
    ("2023-04-12 09:10:00", "Took a detour to run a quick errand downtown."),
    ("2023-04-12 09:20:00", "Follow up on the gym membership renewal."),
    ("2023-04-12 09:30:00", "Noticed an unusual graffiti mark on the alley wall."),
    ("2023-04-12 09:40:00", "The city’s background noise is a mix of honks and chatter."),
    ("2023-04-12 09:50:00", "Grabbed a quick lunch on the run."),
    ("2023-04-12 10:00:00", "Check on the package delivery status online."),
    ("2023-04-12 10:10:00", "Ponder if busy days make time feel slower."),
    ("2023-04-12 10:20:00", "Felt a sudden drop in the ambient temperature."),
    ("2023-04-12 10:30:00", "Helped a neighbor with a minor task."),
    ("2023-04-12 10:40:00", "Remember to review the news headlines later."),
    ("2023-04-12 10:50:00", "Wonder if these scattered notes add up to a coherent day."),
    ("2023-04-12 11:00:00", "Checked the weather and confirmed a clear, sunny day."),
    ("2023-04-12 11:05:00", "Grabbed a small snack at a corner cafe to reenergize."),
    ("2023-04-12 11:10:00", "Called the bank and resolved the billing query."),
    ("2023-04-12 11:15:00", "Sent a follow-up email regarding the pending project update."),
    ("2023-04-12 11:20:00", "Checked the meeting message and prepared notes for tomorrow."),
    ("2023-04-12 11:25:00", "Picked up a new charger at the electronics store."),
    ("2023-04-12 11:30:00", "Renewed the gym membership with a quick online call."),
    ("2023-04-12 11:35:00", "Verified the package delivery status; it's scheduled for tomorrow."),
    ("2023-04-12 11:40:00", "Reviewed the morning news headlines; most stories were uplifting."),
    ("2023-04-12 12:00:00", "Had lunch—a light sandwich and some quiet time."),
    ("2023-04-12 12:30:00", "Noticed the park fountain quietly splashing water, a simple delight."),
    ("2023-04-12 13:00:00", "Took a stroll through the neighborhood, enjoying a brief break."),
    ("2023-04-12 13:30:00", "Observed a street performer entertaining a small crowd."),
    ("2023-04-12 14:00:00", "Stopped to chat briefly with a friend over coffee."),
    ("2023-04-12 14:30:00", "Saw a playful reflection in a shop window and smiled."),
    ("2023-04-12 15:00:00", "Detoured home to pick up a forgotten jacket."),
    ("2023-04-12 15:30:00", "Jotted down an interesting idea that came up during the day."),
    ("2023-04-12 16:00:00", "Glanced at the sky and admired the soft hues of the afternoon."),
    ("2023-04-12 16:30:00", "Paused to appreciate the rhythm of the city life."),
    ("2023-04-12 17:00:00", "Returned home and tidied up the workspace."),
    ("2023-04-12 17:30:00", "Made a quick call to confirm dinner plans with a friend."),
    ("2023-04-12 18:00:00", "Prepared dinner while listening to favorite tunes."),
    ("2023-04-12 18:30:00", "Wrapped up pending tasks and cleared the day's to-do list."),
    ("2023-04-12 19:00:00", "Went for a short walk outside, enjoying the evening air."),
    ("2023-04-12 19:30:00", "Noticed the first stars appearing in the darkening sky."),
    ("2023-04-12 20:00:00", "Relaxed with a book, winding down from the busy day."),
    ("2023-04-12 20:30:00", "Recapped the day’s events and tasks, feeling accomplished."),
    ("2023-04-12 21:00:00", "Started preparing for bed and unwinding."),
    ("2023-04-12 21:30:00", "Noticed the gentle hum of the night settling in."),
    ("2023-04-12 22:00:00", "Set the alarm and tidied up lingering details."),
    ("2023-04-12 22:30:00", "Drifted off to sleep, looking forward to tomorrow."),
]

@pytest.fixture(scope="function")
def notes(setup_database):
    notes = []
    for timestamp, note_text in notes_sample:
        note = db.Note.create(
            note_text,
            timestamp=timestamp,
        )
        notes.append(note)
    return notes

def test_processor(notes):
    # get the first note, the way we would in our scheduler
    initial_note = db.Note.get_next_unprocessed_note()
    assert initial_note is not None
    assert initial_note.note_text == notes[0].note_text
    assert initial_note.timestamp == notes[0].timestamp
    # initialize the processor
    note_processor = processor.NoteProcessor(initial_note)
    # process the note
    note_processor.process()
    assert initial_note.processed_note_text is not None
    # The first note is an action, about waking up
    assert note_processor.category is not None
    assert note_processor.category.name == "action"
    assert note_processor.annotation is not None
    assert note_processor.annotation.note_id == initial_note.id
    assert note_processor.annotation.category_id == note_processor.category.id
    # an action should have been created
    assert note_processor.action is not None
    assert note_processor.action.id > 0
    assert note_processor.action.source_note_id == note_processor.annotation.id
    assert note_processor.action.start_time == initial_note.timestamp
    
    # lets do the next note
    second_note = db.Note.get_next_unprocessed_note()
    assert second_note is not None
    assert second_note.note_text == notes[1].note_text
    assert second_note.timestamp == notes[1].timestamp
    # initialize the processor
    note_processor = processor.NoteProcessor(second_note)
    # process the note
    note_processor.process()
    assert second_note.processed_note_text is not None
    # The second note is an observation, about a strange noise
    assert note_processor.category is not None
    assert note_processor.category.name == "observation"
    assert note_processor.annotation is not None
    assert note_processor.annotation.note_id == second_note.id
    assert note_processor.annotation.category_id == note_processor.category.id
    # no observation object exists so no further checks

    # next note
    third_note = db.Note.get_next_unprocessed_note()
    assert third_note is not None
    assert third_note.note_text == notes[2].note_text
    assert third_note.timestamp == notes[2].timestamp
    # initialize the processor
    note_processor = processor.NoteProcessor(third_note)
    # process the note
    note_processor.process()
    # the third note is a todo
    assert note_processor.category is not None
    assert note_processor.category.name == "todo"
    assert note_processor.annotation is not None
    assert note_processor.annotation.note_id == third_note.id
    assert note_processor.annotation.category_id == note_processor.category.id
    # a todo should have been created
    assert note_processor.todo is not None
    assert note_processor.todo.id > 0
    assert note_processor.todo.source_note_id == note_processor.annotation.id
    # no time was mentioned, so there should be no time data
    assert note_processor.todo.target_start_time == None
    check_weather_todo = note_processor.todo

    # lets do the next note
    fourth_note = db.Note.get_next_unprocessed_note()
    assert fourth_note is not None
    assert fourth_note.note_text == notes[3].note_text
    assert fourth_note.timestamp == notes[3].timestamp
    # initialize the processor
    note_processor = processor.NoteProcessor(fourth_note)
    # process the note
    note_processor.process()
    assert fourth_note.processed_note_text is not None
    # The fourth note is an action against the previous todo, but it was phrased as an observation
    assert note_processor.category is not None
    assert note_processor.category.name == "observation"
    assert note_processor.annotation is not None
    assert note_processor.annotation.note_id == fourth_note.id
    assert note_processor.annotation.category_id == note_processor.category.id

    # the next one is a command that should update the previous one. 
    fifth_note = db.Note.get_next_unprocessed_note()
    assert fifth_note is not None
    assert fifth_note.note_text == notes[4].note_text
    assert fifth_note.timestamp == notes[4].timestamp
    # initialize the processor
    note_processor = processor.NoteProcessor(fifth_note)
    # process the note
    note_processor.process()
    assert fifth_note.processed_note_text is not None
    # The fifth note is a command to update the previous todo
    assert note_processor.category is not None
    assert note_processor.category.name == "command"
    assert note_processor.annotation is not None
    assert note_processor.annotation.note_id == fifth_note.id
    assert note_processor.annotation.category_id == note_processor.category.id
    # a command should have been created
    assert note_processor.command is not None
    assert note_processor.command.source_note_id == note_processor.annotation.id
    assert note_processor.command.command_text == "update_note_category"
    assert note_processor.command.value_before == "observation"
    assert note_processor.command.desired_value == "action"
    assert note_processor.command.target_id == fourth_note.id
    # This should have updated the category of the previous todo
    updated_annotation = db.Annotation.get_by_source_note_id(fourth_note.id)
    assert updated_annotation is not None
    assert updated_annotation.category.name == "action"

    # now lets run a cycle of our secondary loop, to re-process annotations
    reprocess_annotation = db.Annotation.get_next_reprocess_candidate()
    assert reprocess_annotation is not None
    assert reprocess_annotation.note_id == fourth_note.id
    assert reprocess_annotation.category.name == "action"
    # initialize the processor
    reprocess_note = reprocess_annotation.note
    assert reprocess_note is not None
    assert reprocess_note.note_text == fourth_note.note_text
    assert reprocess_note.timestamp == fourth_note.timestamp
    # initialize the processor
    note_processor = processor.NoteProcessor(reprocess_note)
    # add the category and annotation to the processor to activate that flow
    note_processor.category = reprocess_annotation.category
    note_processor.annotation = reprocess_annotation
    # reprocess the note
    note_processor.process()
    assert reprocess_note.processed_note_text is not None
    # make sure it marked the annotation as reprocessed so we don't loop indefinitely
    assert note_processor.annotation.reprocess == False
    # The reprocessed note is an action, about checking the weather
    assert note_processor.category is not None
    assert note_processor.category.name == "action"
    assert note_processor.annotation is not None
    assert note_processor.annotation.note_id == reprocess_note.id
    assert note_processor.annotation.category_id == note_processor.category.id
    # an action should have been created
    assert note_processor.action is not None
    assert note_processor.action.source_note_id == note_processor.annotation.id
    assert note_processor.action.start_time == reprocess_note.timestamp
    # the note was previously categorized as an observation, so nothing to 
    # make sure is deleted
    # lets check and see if that todo was completed
    completed_todo = db.Todo.get_by_id(check_weather_todo.id)
    assert completed_todo is not None
    assert completed_todo.complete == True

    # lets do the next note
    sixth_note = db.Note.get_next_unprocessed_note()
    assert sixth_note is not None
    assert sixth_note.note_text == notes[5].note_text
    assert sixth_note.timestamp == notes[5].timestamp
    # initialize the processor
    note_processor = processor.NoteProcessor(sixth_note)
    # process the note
    note_processor.process()
    assert sixth_note.processed_note_text is not None
    # The sixth note is an action, about making coffee
    assert note_processor.category is not None
    assert note_processor.category.name == "action"
    assert note_processor.annotation is not None
    assert note_processor.annotation.note_id == sixth_note.id
    assert note_processor.annotation.category_id == note_processor.category.id
    # an action should have been created
    assert note_processor.action is not None
    assert note_processor.action.source_note_id == note_processor.annotation.id
    assert note_processor.action.start_time == sixth_note.timestamp






    
    
