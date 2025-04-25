# we will import a newly created get_client equivalent, it will just give us the OpenAI client
from ..llm import get_light_client
# we will import the various functions and and respective schemas from their files in this directory
from .annotate_note import annotate_note, annotate_note_tool
# we will define a processor class
# we will assign the function schemas to a tools property
# we will process the notes in the following sequence: 
# 1. pass the raw note to a chatbot along with the last two hours (or 25, whichever is more), open todos, and actions from the past two hours
# 1a. the chatbot will be presented with tooling to categorize, annotate, and create spinoff objects
# 1b. the chatbot will have a tool to get additional context, if an action or command is created.
# ###NOTE: I need to create a new DB object for curiosities

# 2. if 1b is the case, the chatbot will be passed todos in chunks of 20 of the items at a time that it will try to find the ID of.
# 2a. run a loop until the chatbot returns a valid id or the max number of tries is reached
# 3. after the command is routed, create a new object in the DB, (make a new table)
