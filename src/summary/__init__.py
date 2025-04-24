from datetime import datetime
import logging
from typing import Tuple

from ..llm import get_client
from ..rendering import strf_notes
from ..db import Note
from ..util import format_time

logger = logging.getLogger(__name__)


def get_summary(prompt: str) -> Tuple[str, str]:
    """
    gets a summary of the given prompt
    """
    logger.info('getting summary for prompt: ' + prompt)
    # determine what the user wants (what timeframe, and of what)
    intent_client = get_client()
    intent_client.load_system_message("get_summary_timeframe", current_time=format_time(datetime.now()))
    response = intent_client.chat(prompt)
    start_time = response.get('start_time')
    if not start_time:
        raise ValueError(f"Start time not found in response: {response}")
    end_time = response.get('end_time')
    if not end_time:
        raise ValueError(f"End time not found in response: {response}")
    # load the context
    notes = Note.get_all(after=start_time, before=end_time, limit=100)
    context_str = strf_notes(notes)
    # get the summary
    summary_client = get_client()
    summary_client.load_system_message("get_summary", current_time=format_time(datetime.now()), context=context_str)
    response = summary_client.chat(prompt)
    summary = response.get('summary')
    if not summary:
        raise ValueError(f"Summary not found in response: {response}")
    title = response.get('title')
    if not title:
        raise ValueError(f"Title not found in response: {response}")
    return title, summary
    

