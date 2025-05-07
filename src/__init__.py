import logging
import logging.config
from pathlib import Path


from . import (
        db, 
        processor,
        config,
        rendering,
        util as utils, 
        categories
)
from .bulk_upload import bulk_upload_notes_list
from .web import rest_server
from .summary import get_summary
from .logging import get_logger


logger = get_logger(__name__)

logger.info("Initializing Database")
db.ensure_tables()
