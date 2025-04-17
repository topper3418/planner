from datetime import datetime

from .config import TIMESTAMP_FORMAT


def parse_time(time_str: str) -> datetime:
    """
    Parse a time string into a standard format.
    """
    return datetime.strptime(time_str, TIMESTAMP_FORMAT)

def format_time(time: datetime) -> str:
    """
    Format a time into a standard string format.
    """
    return datetime.strftime(time, TIMESTAMP_FORMAT)
