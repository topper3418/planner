import logging
from pprint import pformat
from typing import List
from openai.types.responses import ToolParam 
# we will import a newly created get_client equivalent, it will just give us the OpenAI client
from ..llm import get_light_client
from ..util import NL
from ..db import Note, Annotation, Action, Todo
from ..rendering import strf_action_light, strf_todo_light, strf_note_light
# we will import the various functions and and respective schemas from their files in this directory
from .annotate_note import annotate_note, get_annotate_note_tool
from .create_action import create_action, get_create_action_tool
from .create_todo import create_todo, get_create_todo_tool
from .find_todo import find_todo, get_find_todo_tool
# we will define a processor class

logger = logging.getLogger(__name__)

# moving this to outside of the class for unit testing purposes
annotation_system_prompt_template = """
You are a world class note taking assistant. The user will create notes throughout the day. You will be fed the notes one at a time, and be tasked with processing them.

For context, you will be given a chunk of the most recent notes, actions, and todos from past annotations.

here are the notes: 

{notes}

here are the actions:

{actions}

here are the todos:

{todos}
"""


class NoteProcessor:
    def __init__(self, note: Note):
        self.note = note
        self.client = get_light_client()
        self.context_notes = Note.get_all(limit=25)
        self.context_actions = Action.get_all(limit=25)
        self.context_todos = Todo.get_all(limit=25, complete=False)
        self.annotate_note_tool = get_annotate_note_tool()
        self.create_action_tool = get_create_action_tool(self.context_todos)
        self.create_todo_tool = get_create_todo_tool()
# we will assign the function schemas to a tools property
        self.annotation_tools: List[ToolParam] = [
            self.annotate_note_tool,
            self.create_action_tool,
            self.create_todo_tool
        ]
        logger.info(f"Tools:\n{pformat(self.annotation_tools)}")
        logger.info(f"Generated system prompt with {len(self.context_notes)} notes, {len(self.context_actions)} actions, and {len(self.context_todos)} todos.")
# 1. pass the raw note to a chatbot along with the last two hours (or 25, whichever is more), open todos, and actions from the past two hours
        self.annotation_system_prompt = annotation_system_prompt_template.format(
            notes=NL.join(strf_note_light(note) for note in self.context_notes) if self.context_notes else "No notes found.",
            actions=NL.join(strf_action_light(action) for action in self.context_actions) if self.context_actions else "No actions found.",
            todos=NL.join(strf_todo_light(todo) for todo in self.context_todos) if self.context_todos else 'No todos found.'
        )

# we will process the notes in the following sequence: 
    def process_annotation(self):
# 1a. the chatbot will be presented with tooling to categorize, annotate, and create spinoff objects
        response = self.client.responses.create(
            model="gpt-4.1",
            instructions=self.annotation_system_prompt,
            input=self.note.model_dump_json(),
            tools=self.annotation_tools,
        )
        from pprint import pprint
        pprint(response.model_dump())


# 1b. the chatbot will have a tool to get additional context, if an action or command is created.
# 2. if 1b is the case, the chatbot will be passed todos in chunks of 20 of the items at a time that it will try to find the ID of.
# 2a. run a loop until the chatbot returns a valid id or the max number of tries is reached
# 3. after the command is routed, create a new object in the DB, (make a new table)
