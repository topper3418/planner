import logging
from typing import Optional
from .rotating_file_handler import attach_rolling_file_handler
from .console_handler import attach_console_handler


def get_logger(logger_name: str, additional_logfile: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    attach_console_handler(logger)
    attach_rolling_file_handler(logger)
    if additional_logfile:
        attach_rolling_file_handler(logger, additional_logfile)
    return logger

