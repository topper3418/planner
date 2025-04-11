import logging

from .note import Note
from .category import Category, default_categories
from .annotation import Annotation
from .action import Action
from .todo import Todo
from .command import Command

logger = logging.getLogger(__name__)


def ensure_tables():
    logger.debug("ensuring tables...")
    Note.ensure_table()
    Category.ensure_table()
    Annotation.ensure_table()
    Action.ensure_table()
    Todo.ensure_table()
    Command.ensure_table()
    logger.info("tables ensured.")


def insert_default_categories():
    logger.debug("inserting default categories...")
    for category in default_categories:
        # Check if the category already exists
        try:
            Category.find_by_name(category.name)
            logger.debug(f"Category '{category.name}' already exists. Skipping insertion.")
            continue
        except ValueError:
            Category.create(
                category.name,
                description=category.description,
                color=category.color,
            )
    logger.info("default categories inserted.")
