import logging
import logging.config
from pathlib import Path


from . import (
        db, 
        processor, 
        processor_v2,
        config,
        rendering,
        util as utils, 
        setup_logging,
        categories
)
from .bulk_upload import bulk_upload_notes_list
from .web import rest_server
from .summary import get_summary


# both the data and log directories are created if they do not exist
log_dir = Path("data/log")
log_dir.mkdir(parents=True, exist_ok=True)


logger = logging.getLogger(__name__)

logger.info("Initializing Database")
db.ensure_tables()
