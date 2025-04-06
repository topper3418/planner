import logging

from .note import Note
from .tag import Tag, default_tags
from .annotation import Annotation

logger = logging.getLogger(__name__)


def ensure_tables():
    logger.debug("ensuring tables...")
    Note.ensure_table()
    Tag.ensure_table()
    Annotation.ensure_table()
    logger.info("tablse ensured.")


def insert_default_tags():
    logger.debug("inserting default tags...")
    for tag in default_tags:
        Tag.create(
            tag.name,
            description=tag.description,
            color=tag.color,
        )
    logger.info("default tags inserted.")
