import logging


from .db import *
from .processor import *
from .config import *
from . import util as utils


# global logging setup

# Custom filter
class SrcFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith('src.')

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Add the filter to the handler
src_filter = SrcFilter()
console_handler.addFilter(src_filter)

# Configure logging
logging.basicConfig(level=logging.DEBUG, handlers=[console_handler])

