# this  module will support the ability to take items from the database
# and convert them to text for printing. 
# this will sort of be like parameterized view getting.
from .note import strf_notes, json_note, strf_note_light, json_note_light
from .action import strf_actions, json_action, strf_action_light
from .todo import strf_todos, json_todo, strf_todo_light
from .curiosity import strf_curiosities, json_curiosity

def banner(text: str, width: int = 75) -> str:
    """
    returns a banner like this
    =================================================================
    ||                           BANNER                            ||
    =================================================================
    """
    top = "=" * width
    side = "||"
    text = text.center(width - len(side) * 2)
    return f"{top}\n{side}{text}{side}\n{top}"








