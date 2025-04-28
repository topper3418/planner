from ..db import Category


def strf_category_light(category: Category) -> str:
    """
    Render a category as a string.
    """
    return f"\t - {category.name} - {category.description}"



