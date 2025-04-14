import logging
import logging.config
from pathlib import Path


from . import (
        util as utils, 
        db, 
        processor, 
        config,
        pretty_printing,
)
from .bulk_upload import bulk_upload_notes_list
from .rest import rest_server


# both the data and log directories are created if they do not exist
log_dir = Path("data/log")
log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "standard",
            "filename": str(log_dir / "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,      # Keep 5 backup files
            "encoding": "utf8",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
}

# Apply the configuration
logging.config.dictConfig(logging_config)

logger = logging.getLogger(__name__)

logger.info("Initializing Database")
db.ensure_tables()
db.ensure_default_categories()
