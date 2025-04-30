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
    "note_text,note_timestamp,expected_todo_target_start_time,expected_todo_target_start_time_range,expected_todo_target_end_time,expected_todo_target_end_time_range,expected_parent_todo_text",
    [
        (
            "To finish my coding project, I will need to create a test suite",
            "2023-10-01 17:00:00",
            None,
            None,
            None,
            None,
            "finish my coding project"
        ),
        (
            "I need to finish my coding project by 5pm",
            "2023-10-01 17:00:00",
            None,
            None,
            "2023-10-01 17:00:00",
            None,
            "finish my coding project"
        ),
        (
            "I need to finish my coding project by 5pm tomorrow",
            "2023-10-01 17:00:00",
            None,
            None,
            "2023-10-02 17:00:00",
            None,
            "finish my coding project"
        ),
        (
            "In order to do the laundry, I need to go to the store to get detergent",
            "2023-10-01 17:00:00",
            None,
            None,
            None,
            None,
            "do laundry"
        ),
        (
            "before I change the oil in my truck, I need to run to autozone",
            "2023-10-01 17:00:00",
            None,
            None,
            None,
            None,
            "change the oil in the truck"
        )
    ]
)
def test_create_todo(
        sample_todos, 
        note_text, 
        note_timestamp, 
        expected_todo_target_start_time, 
        expected_todo_target_start_time_range,
        expected_todo_target_end_time,
        expected_todo_target_end_time_range,
        expected_parent_todo_text
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
        tools=[processor.get_create_todo_tool()],
    )
    assert response.output, f"Response should not be None for note: {note_text}"
    output_names = [output.name for output in response.output]
    assert 'create_todo' in output_names, (
        f"create_todo tool should be in the response for note: {note_text}. "
        f"Output names: {output_names}"
    )
    assert response.output, f"Response should not be None for note: {note_text}"
    create_todo_output = response.output[0]
    assert create_todo_output.arguments
    create_todo_args = json.loads(create_todo_output.arguments)
    todo_text = create_todo_args.get('todo_text')
    assert todo_text, (
        f"Todo text should not be None for note: {note_text}. "
        f"Output: {create_todo_args}"
    )
    target_start_time_str = create_todo_args.get('target_start_time')
    if expected_todo_target_start_time:
        assert target_start_time_str, (
            f"Start time should not be None for note: {note_text}. "
            f"Output: {create_todo_args}"
        )
        assert target_start_time_str == expected_todo_target_start_time, (
           f"Expected start time {expected_todo_target_start_time}, but got {target_start_time_str}"
        )
    elif expected_todo_target_start_time_range:
        assert target_start_time_str, (
            f"Start time should not be None for note: {note_text}. "
            f"Output: {create_todo_args}"
        )
        expected_start_time_str, expected_end_time_str = expected_todo_target_start_time_range
        start_time = utils.parse_time(target_start_time_str)
        expected_start_time = utils.parse_time(expected_start_time_str)
        expected_end_time = utils.parse_time(expected_end_time_str)
        assert expected_start_time <= start_time <= expected_end_time, (
            f"Expected start time {expected_start_time} <= {start_time} <= {expected_end_time}"
        )
    else:
        assert target_start_time_str is None, (
            f"Start time should be None for note: {note_text}. "
            f"Output: {create_todo_args}"
        )
    target_end_time_str = create_todo_args.get('target_end_time')
    if expected_todo_target_end_time:
        assert target_end_time_str, (
            f"End time should not be None for note: {note_text}. "
            f"Output: {create_todo_args}"
        )
        assert target_end_time_str == expected_todo_target_end_time, (
            f"Expected end time {expected_todo_target_end_time}, but got {target_end_time_str}"
        )
    elif expected_todo_target_end_time_range:
        assert target_end_time_str, (
            f"End time should not be None for note: {note_text}. "
            f"Output: {create_todo_args}"
        )
        expected_start_time_str, expected_end_time_str = expected_todo_target_end_time_range
        start_time = utils.parse_time(target_end_time_str)
        expected_start_time = utils.parse_time(expected_start_time_str)
        expected_end_time = utils.parse_time(expected_end_time_str)
        assert expected_start_time <= start_time <= expected_end_time, (
            f"Expected end time {expected_start_time} <= {start_time} <= {expected_end_time}"
        )
    else:
        assert target_end_time_str is None, (
            f"End time should be None for note: {note_text}. "
            f"Output: {create_todo_args}"
        )
    parent_id = create_todo_args.get('parent_id')
    if expected_parent_todo_text and expected_parent_todo_text != "N/A":
        assert parent_id, (
            f"Parent ID should not be None for action '{todo_text}'. "
            f"Output: {create_todo_args}"
        )
        expected_parent_todo = db.Todo.get_all(search=expected_parent_todo_text)[0]
        assert parent_id == expected_parent_todo.id, (
            f"Expected todo ID {expected_parent_todo.id}, but got {parent_id}"
        )
    else:
        assert parent_id is None, (
            f"Parent ID should be None for note: {note_text}. "
            f"Output: {create_todo_args}"
        )

