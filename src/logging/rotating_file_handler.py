
from logging import Logger
from logging.handlers import RotatingFileHandler

from .log_path import LOGS_DIR
from .formatter import formatter


def attach_rolling_file_handler(logger: Logger, log_filename: str = 'planner.log'):
    handler = RotatingFileHandler(
        LOGS_DIR / log_filename, maxBytes=50 * 1024 * 1024, backupCount=5
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

