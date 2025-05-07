import logging

from .formatter import formatter


def attach_console_handler(logger: logging.Logger):
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

