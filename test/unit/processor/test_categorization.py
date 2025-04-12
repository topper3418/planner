import pytest

from src import db, processor


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


def test_categorize_notes(setup_database):
    # create a test note to work with
    for category_name, notes in notes_categories.items():
        success_obj = {
            "success": 0,
            "fail": 0
        }
        success_rate = {
            "action": success_obj.copy(),
            "todo": success_obj.copy(),
            "curiosity": success_obj.copy(),
            "observation": success_obj.copy(),
            "command": success_obj.copy()
        }
        for note_text in notes:
            note = db.Note.create(note_text)
            category = processor.categorize_note(note)
            assert category is not None
            if category.name == category_name:
                success_rate[category_name]["success"] += 1
            else:
                print(f"Failed to categorize note: {note_text}. Expected {category_name}, got {category.name}")
                success_rate[category_name]["fail"] += 1
        assert success_rate["action"]["fail"] == 0
        assert success_rate["todo"]["fail"] == 0
        assert success_rate["curiosity"]["fail"] == 0
        assert success_rate["observation"]["fail"] == 0
        assert success_rate["command"]["fail"] == 0
