from datetime import datetime
from typing import Tuple

from ..logging import get_logger
from ..llm import get_client
from ..rendering import strf_notes
from ..db import Note
from ..util import format_time

logger = get_logger(__name__, "summary.log")


summary_timeframe_system_message_template = """
Your job is to take in a prompt from the user, and determine for what timeframe they want to summarize. 
 - the time based fields should be in the format of "%Y-%m-%d %H:%M:%S"
 - they will likely use a referential time for their prompt, like "Summarize what I did today" or "summarize what I did last week". Use the current timestamp as a reference to give a full date and time for the time fields.

current time: {current_time}

you will respond in with a json object with the following format:

{{
    "start_time": "start time",  # format: "%Y-%m-%d %H:%M:%S", beginning bounds for the summary
    "end_time": "end time",  # format: "%Y-%m-%d %H:%M:%S", ending bounds for the summary
}}
"""

get_summary_system_message_template = """
Your job is to take in a summary request from the user, consider the context, and return the summary as well as a title for the summary.
 - do not extrapolate or hallucinate any events or information, just use what they gave you. For example if they ask for what they did that week but there are no objects for monday and tuesday, do not make anything up for what they might have done those days, just leave it out or note that there is no data for those days.
 - give the summary in markdown format 
 - comply with any of the users formatting requests (bulleted/numbered lists, cause->effect, etc)
 - if the user asks for any kind of time series, they likely want each time bucket to be listed out with bullet points for that bucket. They will also want it in chronological order, with the earliest time bucket first.
 - pay special attention to the categories of the notes with respect to their query. For example, if they are wondering what they did, prioritize actions. if they are wondering about things they need or needed to get done, prioritize todos. if the user asks about what they were curious about, do not include what they got done or what they wanted to get done, just what they were curious about. 
 - Unless the user asks for it, do not include bulleted lists for each category of note, your job is to condense not inform. 
 - keep your response as concise as possible to still give an accurate account of what the user wants to know about their notes.

For your reference, the current time is: {current_time}

The context given will be a list of notes, from which you will generate the summary

{context}

please return your response in the following format: 

{{
    "title": "an appropriate title for the summary",
    "summary": "your summary",
}}
"""


def get_summary(prompt: str) -> Tuple[str, str]:
    """
    gets a summary of the given prompt
    """
    logger.info("getting summary for prompt: " + prompt)
    # determine what the user wants (what timeframe, and of what)
    intent_client = get_client()
    intent_client.load_system_message(
        summary_timeframe_system_message_template,
        current_time=format_time(datetime.now()),
    )
    response = intent_client.chat(prompt)
    start_time = response.get("start_time")
    if not start_time:
        raise ValueError(f"Start time not found in response: {response}")
    end_time = response.get("end_time")
    if not end_time:
        raise ValueError(f"End time not found in response: {response}")
    # load the context
    notes = Note.get_all(after=start_time, before=end_time, limit=100)
    context_str = strf_notes(notes)
    # get the summary
    summary_client = get_client()
    summary_client.load_system_message(
        get_summary_system_message_template,
        current_time=format_time(datetime.now()),
        context=context_str,
    )
    response = summary_client.chat(prompt)
    summary = response.get("summary")
    if not summary:
        raise ValueError(f"Summary not found in response: {response}")
    title = response.get("title")
    if not title:
        raise ValueError(f"Title not found in response: {response}")
    return title, summary
