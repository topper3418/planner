import logging

from .note import Note
from .category import Category, default_categories
from .annotation import Annotation

logger = logging.getLogger(__name__)


def ensure_tables():
    logger.debug("ensuring tables...")
    Note.ensure_table()
    Category.ensure_table()
    Annotation.ensure_table()
    logger.info("tablse ensured.")


def insert_default_categories():
    logger.debug("inserting default categories...")
    for category in default_categories:
        Category.create(
            category.name,
            description=category.description,
            color=category.color,
        )
    logger.info("default categories inserted.")
