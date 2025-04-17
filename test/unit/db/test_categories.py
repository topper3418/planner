import pytest

from src import db

def test_category_insertion(setup_database):
    # make sure the category were inserted correctly
    categories = db.Category.get_all()
    assert len(categories) > 0
    assert all(category.id is not None for category in categories)
    category_names = [category.name for category in categories]
    assert "action" in category_names
    assert "todo" in category_names
    assert "curiosity" in category_names
    assert "observation" in category_names
    assert "command" in category_names
    category_descriptions = [category.description for category in categories]
    assert not any(description is None for description in category_descriptions)

def test_save_category(setup_database):
    # Test saving a new category
    category = db.Category.find_by_name("action")
    assert category is not None
    assert category.name == "action"
    category.description = "Test description"
    category.save()
    category.reload()
    assert category.description == "Test description"
    category.color = "red"
    category.save()
    category.reload()
    assert category.color == "red"

def test_fetch_categories(setup_database):
    # Test fetching all categories
    categories = db.Category.get_all()
    assert len(categories) > 0
    first_category = categories[0]
    assert first_category.id is not None
    first_category_copy = db.Category.get_by_id(first_category.id)
    assert first_category_copy is not None
    assert first_category_copy.id == first_category.id
    assert first_category_copy.name == first_category.name
    assert first_category_copy.description == first_category.description
    last_category = categories[-1]
    assert last_category.id is not None
    last_category_copy = db.Category.get_by_id(last_category.id)
    assert last_category_copy is not None
    assert last_category_copy.id == last_category.id
    assert last_category_copy.name == last_category.name
    assert last_category_copy.description == last_category.description
    all_ids = set(category.id for category in categories)
    max_id = max(all_ids)
    with pytest.raises(ValueError):
        db.Category.get_by_id(max_id + 1)

def test_find_category_by_name(setup_database):
    # Test finding a category by name
    category = db.Category.find_by_name("action")
    assert category is not None
    assert category.name == "action"
    assert category.description is not None
    assert category.color is not None
    # Test finding a non-existent category
    with pytest.raises(ValueError):
        db.Category.find_by_name("non_existent_category")
