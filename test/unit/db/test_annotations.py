import pytest

from src import db


@pytest.fixture
def sample_annotations(setup_database):
    # reset the database
    db.teardown()
    db.init_db()
    db.ensure_default_categories()
    note = db.Note.create(
        "I just woke up",
        timestamp="2023-04-12 12:00:00",
    )
    category = db.Category.get_by_name("action")
    # create the annotation
    annotation = db.Annotation.create(
        note.id,
        category.id,
        "Test annotation",
    )
    return note, category, annotation


def test_annotation_props(sample_annotations):
    note, category, annotation = sample_annotations
    assert note is not None
    assert note.id is not None
    assert note.note_text == "I just woke up"
    assert category is not None
    assert category.name == "action"
    assert annotation is not None
    assert annotation.id is not None
    assert annotation.note_id == note.id
    assert annotation.category_id == category.id
    assert annotation.annotation_text == "Test annotation"
    # make sure the note is fetched correctly
    assert note.id == annotation.note.id
    assert note.note_text == annotation.note.note_text
    assert note.timestamp == annotation.note.timestamp
    # make sure the category is fetched correctly
    assert category.id == annotation.category.id
    assert category.name == annotation.category.name
    assert category.description == annotation.category.description
    assert category.color == annotation.category.color


def test_annotation_save(sample_annotations):
    note, category, annotation = sample_annotations
    # update the annotation
    annotation.annotation_text = "Updated annotation"
    annotation.save()
    annotation.reload()
    # make sure the update worked
    assert annotation.annotation_text == "Updated annotation"
    # make sure the reload worked with a new fetch
    annotation_doublecheck = db.Annotation.get_by_id(annotation.id)
    assert annotation_doublecheck is not None
    assert annotation_doublecheck.annotation_text == "Updated annotation"


def test_annotation_reprocessing(sample_annotations):
    note, category, annotation = sample_annotations
    # test reprocessing
    assert not annotation.reprocess
    annotation.reprocess = True
    annotation.save()
    annotation.reload()
    assert annotation.reprocess
    # make sure the reload worked with the method
    annotation_doublecheck = db.Annotation.get_next_reprocess_candidate()
    assert annotation_doublecheck is not None
    assert annotation_doublecheck.id == annotation.id
    # test the method the other way
    annotation.reprocess = False
    annotation.save()
    annotation_triplecheck = db.Annotation.get_next_reprocess_candidate()
    assert annotation_triplecheck is None


def test_delete_annotation(sample_annotations):
    note, category, annotation = sample_annotations
    # delete the annotation
    annotation.delete()
    # make sure the delete worked
    with pytest.raises(ValueError):
        db.Annotation.get_by_id(annotation.id)
    # make sure the note is still there
    note.reload()
    assert note is not None
    assert note.note_text == "I just woke up"


def test_get_by_note_id(sample_annotations):
    note, category, annotation = sample_annotations
    # test get by note id
    fetched_annotation = db.Annotation.get_by_source_note_id(note.id)
    assert fetched_annotation is not None
    assert fetched_annotation.id == annotation.id
    assert fetched_annotation.note_id == note.id


def test_get_by_category_name(setup_database):
    # reset the database
    db.teardown()
    db.init_db()
    db.ensure_default_categories()
    # test get by category name
    action_category = db.Category.get_by_name("action")
    assert action_category is not None
    assert action_category.name == "action"
    curiosity_category = db.Category.get_by_name("curiosity")
    assert curiosity_category is not None
    assert curiosity_category.name == "curiosity"
    observation_category = db.Category.get_by_name("observation")
    assert observation_category is not None
    assert observation_category.name == "observation"
    todo_category = db.Category.get_by_name("todo")
    assert todo_category is not None
    assert todo_category.name == "todo"
    categories = [
        category.model_dump()
        for category in [
            action_category,
            curiosity_category,
            observation_category,
            todo_category,
        ]
    ]
    from pprint import pformat

    print(f"Categories:\n{pformat(categories)}")
    first_action_annotation = db.Annotation.create(
        note_id=1,
        category_id=action_category.id,
        annotation_text="First action annotation",
    )
    first_curiosity_annotation = db.Annotation.create(
        note_id=2,
        category_id=curiosity_category.id,
        annotation_text="First curiosity annotation",
    )
    second_action_annotation = db.Annotation.create(
        note_id=3,
        category_id=action_category.id,
        annotation_text="Second action annotation",
    )
    first_observation_annotation = db.Annotation.create(
        note_id=4,
        category_id=observation_category.id,
        annotation_text="First observation annotation",
    )
    first_todo_annotation = db.Annotation.create(
        note_id=5,
        category_id=todo_category.id,
        annotation_text="First todo annotation",
    )
    second_curiosity_annotation = db.Annotation.create(
        note_id=6,
        category_id=curiosity_category.id,
        annotation_text="Second curiosity annotation",
    )
    # test get by category name
    action_annotations = db.Annotation.get_by_category_name("action")
    assert len(action_annotations) == 2
    assert (
        action_annotations[1].annotation_text == "First action annotation"
    )
    assert (
        action_annotations[0].annotation_text == "Second action annotation"
    )
    curiosity_annotations = db.Annotation.get_by_category_name("curiosity")
    assert len(curiosity_annotations) == 2
    assert (
        curiosity_annotations[1].annotation_text
        == "First curiosity annotation"
    )
    assert (
        curiosity_annotations[0].annotation_text
        == "Second curiosity annotation"
    )
    observation_annotations = db.Annotation.get_by_category_name(
        "observation"
    )
    assert len(observation_annotations) == 1
    assert (
        observation_annotations[0].annotation_text
        == "First observation annotation"
    )
    todo_annotations = db.Annotation.get_by_category_name("todo")
    assert len(todo_annotations) == 1
    assert todo_annotations[0].annotation_text == "First todo annotation"
