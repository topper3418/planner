import pytest

from src import db, processor_v2 as processor


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
            source_annotation_id=ann_id,
        ),
        db.Todo.create(
            todo_text="talk to the vendor", 
            source_annotation_id=ann_id,
        ),
        db.Todo.create(
            todo_text="change the oil in the truck", 
            source_annotation_id=ann_id,
        ),
        db.Todo.create(
            todo_text="call my mom", 
            source_annotation_id=ann_id,
        ),
        db.Todo.create(
            todo_text="work out today", 
            source_annotation_id=ann_id,
        ),
        db.Todo.create(
            todo_text="do laundry", 
            source_annotation_id=ann_id,
        ),
        db.Todo.create(
            todo_text="clean the house", 
            source_annotation_id=ann_id,
        ),
    ]

#(action_text, correct_todo_search, mark_complete)
test_cases = [
    ("I'm starting on my coding project now", "finish my coding project", False),
    ("I have finished my coding proejct!", "finish my coding project", True),
    ("All done with my coding project", "finish my coding project", True),
    ("I'm going to the gym now", "work out today", False),
    ("I just got back from the gym", "work out today", True),
    ("I just spoke with the vendor. He said he will update hist timeline", "talk to the vendor", True),
    ("I just got off the phone with mom", "call my mom", True),
    ("I'm calling my mom now", "call my mom", False),
    ("I just finished doing laundry", "do laundry", True),
    ("I just finished cleaning the house", "clean the house", True),
    ("I am going to the store for oil for the truck", "change the oil in the truck", False),
    ("The truck's oil is changed", "change the oil in the truck", True),
    ("I just built shelves", "N/A", False),
    ("I just mowed the lawn", "N/A", False),
    ("I am about to brush my teeth", "N/A", False),
]
@pytest.mark.parametrize("action_text,expected_todo_text,mark_complete", test_cases)
def test_find_todo(sample_todos, action_text, expected_todo_text, mark_complete):
    note = db.Note.create(action_text)
    annotation = db.Annotation.create(
        note_id=note.id,
        category_id=1,
        annotation_text="This is a test annotation",
    )
    action = db.Action.create(
        start_time=note.timestamp,
        action_text=action_text,
        source_annotation_id=annotation.id,
    )
    todo_response = processor.find_todo(action)
    if expected_todo_text == "N/A":
        assert todo_response is None, (
            f"Expected no todo to be found for action '{action_text}', but got {todo_response}"
        )
    else:
        assert todo_response is not None, (
            f"Expected a todo to be found for action '{action_text}', but got None"
        )
        todo, mark_complete_response = todo_response
        assert todo.todo_text == expected_todo_text, (
            f"Expected todo text '{expected_todo_text}', but got '{todo.todo_text}'"
        )
        assert mark_complete_response == mark_complete, (
            f"Expected mark_complete '{mark_complete}', but got '{mark_complete_response}'"
        )




