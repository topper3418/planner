import pytest
import json

from src import (
    db, 
    processor_v2 as processor, 
    rendering,
    utils
)


# create a bunch of todos to test with
@pytest.fixture
def sample_todos(refresh_database):
    first_note = db.Note.create("Placeholder")
    first_annotation = db.Annotation.create(
        note_id=first_note.id,
        category_id=1,
        annotation_text="This is a test annotation",
    )
    ann_id = first_annotation.id
    todos = [
        db.Todo.create(
            todo_text="finish my coding project", 
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="talk to the vendor", 
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="change the oil in the truck", 
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="call my mom", 
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="work out today", 
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="do laundry", 
            source_note_id=ann_id,
        ),
        db.Todo.create(
            todo_text="clean the house", 
            source_note_id=ann_id,
        ),
    ]
    return todos

client = processor.get_light_client()

@pytest.mark.parametrize(
    "note_text,note_timestamp,expected_action_start_time,expected_action_start_time_range,expected_todo_text,expected_mark_complete", 
    [
        (
            "I am finished with work for the day",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "N/A",
            False
        ),
        (
            "I have finished my coding project!",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "finish my coding project",
            True
        ),
        (
            "All done with my coding project",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "finish my coding project",
            True
        ),
        (
            "I'm going to the gym now",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "work out today",
            False
        ),
        (
            "I just got back from the gym",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "work out today",
            True
        ),
        (
            "I just spoke with the vendor. He said he will update his timeline",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "talk to the vendor",
            True
        ),
        (
            "I just got off the phone with mom",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "call my mom",
            True
        ),
        (
            "I'm calling my mom now",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "call my mom",
            True
        ),
        (
            "I just finished doing laundry",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "do laundry",
            True
        ),
        (
            "I just finished cleaning the house",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "clean the house",
            True
        ),
        (
            "I am going to the store for oil for the truck",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "change the oil in the truck",
            False
        ),
        (
            "The truck's oil is changed",
            "2023-10-01 17:00:00",
            "2023-10-01 17:00:00",
            None,
            "change the oil in the truck",
            True
        ),
        (
            "I built shelves yesterday", 
            "2023-10-02 17:00:00",
            None, 
            ("2023-10-01 00:00:00", "2023-10-01 23:59:59"), 
            "N/A", 
            False
        ),
        (
            "I mowed the lawn this morning", 
            "2023-10-01 17:00:00",
            None, 
            ("2023-10-01 8:00:00", "2023-10-01 12:00:00"), 
            "N/A", 
            False
        ),
    ]
)
def test_create_action(
        sample_todos, 
        note_text, 
        note_timestamp, 
        expected_action_start_time, 
        expected_action_start_time_range,
        expected_todo_text, 
        expected_mark_complete
):
    note = db.Note.create(
        note_text=note_text,
        timestamp=note_timestamp,
    )
    response = client.responses.create(
        model="gpt-4.1",
        instructions=processor.annotation_system_prompt_template.format(
            notes="no notes found",
            actions="no actions found",
            todos=[rendering.strf_todo_light(todo) for todo in sample_todos],
        ),
        input=note.model_dump_json(),
        tools=[processor.get_create_action_tool(sample_todos)],
    )
    assert response.output, f"Response should not be None for note: {note_text}"
    output_names = [output.name for output in response.output]
    assert 'create_action' in output_names, (
        f"create_action tool should be in the response for note: {note_text}. "
        f"Output names: {output_names}"
    )
    assert response.output, f"Response should not be None for note: {note_text}"
    create_action_output = response.output[0]
    assert create_action_output.arguments
    create_action_args = json.loads(create_action_output.arguments)
    action_text = create_action_args.get('action_text')
    assert action_text, (
        f"Action text should not be None for note: {note_text}. "
        f"Output: {create_action_args}"
    )
    start_time_str = create_action_args.get('action_timestamp')
    assert start_time_str, (
        f"Start time should not be None for note: {note_text}. "
        f"Output: {create_action_args}"
    )
    if expected_action_start_time:
        assert start_time_str == expected_action_start_time, (
            f"Expected start time {expected_action_start_time}, but got {start_time_str}"
        )
    if expected_action_start_time_range:
        expected_start_time_str, expected_end_time_str = expected_action_start_time_range
        start_time = utils.parse_time(start_time_str)
        expected_start_time = utils.parse_time(expected_start_time_str)
        expected_end_time = utils.parse_time(expected_end_time_str)
        assert expected_start_time <= start_time <= expected_end_time, (
            f"Expected start time {expected_start_time} <= {start_time} <= {expected_end_time}"
        )
    todo_id = create_action_args.get('todo_id')
    mark_complete = create_action_args.get('mark_complete')
    if todo_id:
        expected_todo = db.Todo.get_all(search=expected_todo_text)[0]
        assert todo_id == expected_todo.id, (
            f"Expected todo ID {expected_todo.id}, but got {todo_id}"
        )
        assert bool(mark_complete) == expected_mark_complete, (
            f"Expected mark_complete {expected_mark_complete}, but got {mark_complete}"
        )
    else:
        assert expected_todo_text == "N/A", (
            f"Expected todo to be found for action '{action_text}', but got none"
        )

