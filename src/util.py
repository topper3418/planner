from datetime import datetime

def parse_time(time_str: str) -> datetime:
    """
    Parse a time string into a standard format.
    """
    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
