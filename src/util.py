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


def clear_terminal():
    print("\033[H\033[J")


def format_paragraph(text: str, width: int = 75, indents=1) -> str:
    """
    Formats a paragraph to fit within a given width.
    """
    space = width - 8 * indents
    pretty_text = ""
    if len(text) > space:
        pretty_text += "\t" * indents + text[:space] + "\n"
        remainder = text[space:]
        while remainder:
            if len(remainder) > space:
                pretty_text += "\t" * indents + remainder[:space] + "\n"
                remainder = remainder[space:]
            else:
                pretty_text += "\t" * indents + remainder + "\n"
                remainder = ""
    else:
        pretty_text += "\t" * indents + text + "\n"
    return pretty_text


NL = "\n"
