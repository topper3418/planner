import json
import logging
from pprint import pformat
from typing import List
from openai.types.responses import ToolParam

from src.config import CHAT_MODEL
from src.errors import SaveDBObjectError

# we will import a newly created get_client equivalent, it will just give us the OpenAI client
from ..llm import get_light_client
from ..util import NL
from ..db import Note, Action, Todo, ToolCall
from ..rendering import strf_action_light, strf_todo_light, strf_note_light
from ..logging import get_logger

# we will import the various functions and and respective schemas from their files in this directory
from .create_action import create_action, get_create_action_tool
from .create_todo import create_todo, get_create_todo_tool
from .create_curiosity import create_curiosity, get_create_curiosity_tool
from .update_note import update_note, get_update_note_tool
from .update_todo import update_todo, get_update_todo_tool
from .update_action import update_action, get_update_action_tool

# we will define a processor class

logger = get_logger(__name__, "processor.log")
logger.setLevel(logging.DEBUG)


# moving this to outside of the class for unit testing purposes
annotation_system_prompt_template = """
You are a world class note taking assistant. The user will create notes throughout the day. You will be fed the notes one at a time, and be tasked with processing them. Your main job is to 
 - log any actions the user takes along with a precise timestamp as to when they took the actions, using the create_action tool.
 - log any todos the user creates along with timestamps for when they intend to start and finish, when included in the users notes, using the create_todo tool. 
 - Feel free to create as many actions or todos as necessary based on the user's note and the surrounding context. If their note contains two actions, call the create action twice. if their note contains two separate things they need to get done, create two todos.
 Additionally,
 - provide short insights into things the user wonders about (curiosities)
 - the user might ask you to modify an entry in their notebook, so you will be provided the tools to do so.
 - You may have to guess a bit with timestamps. Use the current timestamp provided in the user's note as context to get the full date.

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
        logger.info(f"Processing note: {self.note.note_text}")
        self.client = get_light_client()
        # load context
        self.context_notes = Note.get_all(
            limit=25, before=self.note.timestamp
        )
        self.context_actions = Action.get_all(
            limit=25, before=self.note.timestamp
        )
        self.context_todos = Todo.get_all(
            limit=25, complete=False, before=self.note.timestamp
        )
        # load tools
        self.create_action_tool = get_create_action_tool(
            self.context_todos
        )
        self.create_todo_tool = get_create_todo_tool(self.context_todos)
        self.create_curiosity_tool = get_create_curiosity_tool()
        self.update_note_tool = get_update_note_tool()
        self.update_todo_tool = get_update_todo_tool()
        self.update_action_tool = get_update_action_tool()
        # we will assign the function schemas to a tools property
        self.annotation_tools: List[ToolParam] = [
            self.create_action_tool,
            self.create_todo_tool,
            self.create_curiosity_tool,
            self.update_note_tool,
            self.update_todo_tool,
            self.update_action_tool,
        ]
        logger.debug(
            f"Generated system prompt with {len(self.context_notes)} notes, {len(self.context_actions)} actions, and {len(self.context_todos)} todos."
        )
        # 1. pass the raw note to a chatbot along with the last two hours (or 25, whichever is more), open todos, and actions from the past two hours
        self.annotation_system_prompt = (
            annotation_system_prompt_template.format(
                notes=(
                    NL.join(
                        strf_note_light(note)
                        for note in self.context_notes
                    )
                    if self.context_notes
                    else "No notes found."
                ),
                actions=(
                    NL.join(
                        strf_action_light(action)
                        for action in self.context_actions
                    )
                    if self.context_actions
                    else "No actions found."
                ),
                todos=(
                    NL.join(
                        strf_todo_light(todo)
                        for todo in self.context_todos
                    )
                    if self.context_todos
                    else "No todos found."
                ),
            )
        )

    # we will process the notes in the following sequence:
    def process_note(self) -> List[ToolCall]:
        # 1a. the chatbot will be presented with tooling to categorize, annotate, and create spinoff objects
        response = self.client.responses.create(
            model=CHAT_MODEL,
            instructions=self.annotation_system_prompt,
            input=self.note.model_dump_json(),
            tools=self.annotation_tools,
        )
        logger.info(
            f"Response:\n{pformat([item.model_dump() for item in response.output])}"
        )
        tool_calls = []
        for tool_response in response.output:
            tool_response_json = tool_response.model_dump()
            logger.info(f"Tool response:\n{pformat(tool_response_json)}")
            # get the tool name
            tool_name = tool_response_json.get("name")
            if not tool_name:
                logger.warning("Tool response did not contain a name.")
                continue
            # get the arguments
            args = tool_response_json.get("arguments")
            if not args:
                logger.warning("Tool response did not contain arguments.")
                continue
            args = json.loads(args)
            tool_call_payload = {
                "source_note_id": self.note.id,
                "tool_call": json.dumps(tool_response_json),
            }
            if tool_name == "create_action":
                action = create_action(self.note, **args)
                logger.info(f"created action with id {action.id}")
                tool_call_payload["target_table"] = "actions"
                tool_call_payload["target_id"] = action.id
                tool_call = ToolCall.create(**tool_call_payload)
            elif tool_name == "create_todo":
                todo = create_todo(self.note, **args)
                if todo is None:
                    logger.warning("Failed to create todo.")
                    continue
                logger.info(f"created todo with id {todo.id}")
                tool_call_payload["target_table"] = "todos"
                tool_call_payload["target_id"] = todo.id
                tool_call = ToolCall.create(**tool_call_payload)
            elif tool_name == "create_curiosity":
                curiosity = create_curiosity(self.note, **args)
                logger.info(f"created curiosity with id {curiosity.id}")
                tool_call_payload["target_table"] = "curiosities"
                tool_call_payload["target_id"] = curiosity.id
                tool_call = ToolCall.create(**tool_call_payload)
            elif tool_name == "update_note":
                note = update_note(**args)
                logger.info(f"updated note with id {note.id}")
                tool_call_payload["target_table"] = "notes"
                tool_call_payload["target_id"] = note.id
                tool_call_payload["target"] = note.model_dump_json()
                tool_call = ToolCall.create(**tool_call_payload)
            elif tool_name == "update_todo":
                try:
                    todo = update_todo(**args)
                except SaveDBObjectError as e:
                    logger.error("Error updating todo: %s", e)
                    self.note.processing_error = str(e)
                    self.note.save()
                    continue
                logger.info(f"updated todo with id {todo.id}")
                tool_call_payload["target_table"] = "todos"
                tool_call_payload["target_id"] = todo.id
                tool_call_payload["target"] = todo.model_dump_json()
                tool_call = ToolCall.create(**tool_call_payload)
            elif tool_name == "update_action":
                action = update_action(**args)
                logger.info(f"updated action with id {action.id}")
                tool_call_payload["target_table"] = "actions"
                tool_call_payload["target_id"] = action.id
                tool_call_payload["target"] = action.model_dump_json()
                tool_call = ToolCall.create(**tool_call_payload)
            else:
                logger.warning(f"Unknown tool name: {tool_name}")
                continue
            tool_calls.append(tool_call)
        self.note.processed = True
        self.note.save()
        logger.info(
            f"Processed note {self.note.id} with {len(tool_calls)} tool calls."
        )
        return tool_calls


# 1b. the chatbot will have a tool to get additional context, if an action or command is created.
# 2. if 1b is the case, the chatbot will be passed todos in chunks of 20 of the items at a time that it will try to find the ID of.
# 2a. run a loop until the chatbot returns a valid id or the max number of tries is reached
# 3. after the command is routed, create a new object in the DB, (make a new table)
