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


