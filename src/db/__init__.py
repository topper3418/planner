import logging

from .note import Note
from .topic import Topic, default_topics
from .annotation import Annotation

logger = logging.getLogger(__name__)


def ensure_tables():
    logger.debug("ensuring tables...")
    Note.ensure_table()
    Topic.ensure_table()
    Annotation.ensure_table()
    logger.info("tablse ensured.")


def insert_default_topics():
    logger.debug("inserting default topics...")
    for topic in default_topics:
        Topic.create(
            topic.name,
            description=topic.description,
            color=topic.color,
        )
    logger.info("default topics inserted.")
