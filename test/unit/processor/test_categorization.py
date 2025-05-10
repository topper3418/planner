import pytest
import json

from src import db, processor_v2 as processor, llm
from src.processor_v2.annotate_note import get_annotate_note_tool, annotate_note


notes_categories = {
    "action": [
        "I am finished with work for the day",
        "I pushed my commit",
        "I am going to bed",
        "I am taking a break",
        "I am starting on my garden project",
        "I found and fixed the bug",
        "I am going to the gym",
        "Starting on my project",
        "talked to the wife for a few minutes"
    ],
    "todo": [
        "I need to finish my project",
        "I will talk to the vendor",
        "The truck needs its oil changed",
        "I need to call my mom",
        "I need to work out today", 
        "I need to do laundry",
        "I need to clean the house"
    ],
    "curiosity": [
        "I wonder how many cities there are in the US",
        "Can I use asserts in a pytest fixture?",
        "I wonder how many people are in the world",
        "How do I do tests in golang?"
    ],
    "observation": [
        "I noticed there is a new restaurant in town",
        "The tomatoes are ripe",
        "Today is a sunny day",
        "10 clients crashed the server on a raspberry pi zero W",
        "The truck had its SRS light on today"
    ],
    "command": [
        "Change the note about waking up to an actiion",
        "Update the timestamp for finishing my workout to 1:30"
    ]
}
# Create parameter list for pytest
test_cases = [
    (category, note)
    for category, notes in notes_categories.items()
    for note in notes
]

client = llm.get_light_client()
categories = db.Category.get_all()

@pytest.mark.parametrize("expected_category,note_text", test_cases)
def test_categorize_notes(refresh_database, expected_category, note_text):
    note = db.Note.create(note_text)
    response = client.responses.create(
        model="gpt-4.1",
        instructions=processor.annotation_system_prompt_template.format(
            notes="no notes found",
            actions="no actions found",
            todos="no todos found",
        ),
        input=note.model_dump_json(),
        tools=[get_annotate_note_tool(categories)]
    )
    assert response.output, f"Response should not be None for note: {note_text}"
    output_names = [output.name for output in response.output]
    assert 'annotate_note' in output_names, (
        f"annotate_note tool should be in the response for note: {note_text}. "
        f"Got {output_names}"
    )
    annotation_output = [output for output in response.output if output.name == 'annotate_note'][0]
    assert annotation_output, f"Annotation output should not be None for note: {note_text}"
    assert annotation_output.arguments, f"Arguments should not be None for note: {note_text}"
    annotation_args = json.loads(annotation_output.arguments)
    assert "category_name" in annotation_args, (
        f"category_name should be in the arguments for note: {note_text}. "
        f"Got {annotation_args}"
    )
    assert "annotation_text" in annotation_args, (
        f"annotation_text should be in the arguments for note: {note_text}. "
        f"Got {annotation_args}"
    )
    print("ANNOTATION OUTPUT:", annotation_output.model_dump())
    assert annotation_args["category_name"] == expected_category, (
        f"Failed to categorize note: {note_text}. "
        f"Expected {expected_category}, got {annotation_args['category_name']}"
    )
