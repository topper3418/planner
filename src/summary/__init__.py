from datetime import datetime
import logging

from ..grok import GrokChatClient
from ..pretty_printing import strf_notes, strf_todos, strf_actions, strf_todos
from ..db import Note, Action, Todo

logger = logging.getLogger(__name__)


def get_summary(prompt: str) -> str:
    """
    gets a summary of the given prompt
    """
    # determine what the user wants (what timeframe, and of what)
    intent_client = GrokChatClient()
    intent_client.load_system_message("get_summary_intent", current_time=datetime.now())
    response = intent_client.chat(prompt)
    intended_object = response.get('intended_object')
    if not intended_object:
        raise ValueError(f"Intended object not found in response: {response}")
    start_time = response.get('start_time')
    if not start_time:
        raise ValueError(f"Start time not found in response: {response}")
    end_time = response.get('end_time')
    if not end_time:
        raise ValueError(f"End time not found in response: {response}")
    # load the context
    if intended_object == "notes":
        notes = Note.get_all(after=start_time, before=end_time, limit=100)
        context_str = strf_notes(notes)
    elif intended_object == "todos":
        todos = Todo.get_all(after=start_time, before=end_time, limit=100)
        context_str = strf_todos(todos)
    elif intended_object == "actions":
        actions = Action.get_all(after=start_time, before=end_time, limit=100)
        context_str = strf_actions(actions)
    else:
        logger.error(f"Unknown intended object: {intended_object}")
        raise ValueError(f"Unknown intended object: {intended_object}")
    # get the summary
    summary_client = GrokChatClient()
    summary_client.load_system_message("get_summary", current_time=datetime.now())
    response = summary_client.chat(context_str)
    summary = response.get('summary')
    if not summary:
        raise ValueError(f"Summary not found in response: {response}")
    title = response.get('title')
    if not title:
        raise ValueError(f"Title not found in response: {response}")
    return title, summary
    

