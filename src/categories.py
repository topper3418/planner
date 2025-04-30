from pydantic import BaseModel, Field


class Category(BaseModel):
    """
    Represents a toipc for M2M grouping notes
    """
    name: str = Field(..., description="Name of the category")
    description: str = Field(..., description="Description of the category")
    color: str = Field(..., description="Color of the category")

    def to_string(self):
        return f"\t - {self.name} - {self.description}"


ACTION = Category(
    name="action", 
    description="Documents an action taken by the user. Anything the user says they did, or anything the user says they are about to do in the immediate future This pertains to an action that was taken, not a task to be completed. It also excludes something that seems like an action, but is actually an observation. This does include future tense actions that sounds like I am going to do it immediately. For example, I am -> action, I just -> action, I will later -> not an action", 
    color="blue"
)

TODO = Category(
    name="todo", 
    description="Indicates a user's intention to complete a task. It is the intent to do an an action", 
    color="cyan"
)

CURIOSITY = Category(
    name="curiosity", 
    description="Something the user is curious about, or wants to learn more about. This can be a wondering, or a direct question to the system. I wonder, I am curious about", 
    color="yellow"
)

OBSERVATION = Category(
    name="observation",
    description="Documents something the user has learned or observed. Put another way, it is anything the user puts in that is simply storing a thought. This does not include things that the user has done, a user cannot observe their own action. To clarify a grey area, if it seems like the user is observing the result of something they did, it is an observation.",
    color="magenta"
)

COMMAND = Category(
    name="command",
    description="This is a command from the user to the system. For example, an instruction to change the category of a note directly, or to update an existing todo, updating a note, changing a timeline of something that has already passed. Any time it seems like the user is talking to the system rather than describing something they have done, experienced or need to do is a command. If they are asking the system to change timing, cancel something, change a category, update somethig, it is a command",
    color="red"
)


def get_category(category_name: str):
    """
    Returns the category object for the given category name.
    """
    categories = {
        "action": ACTION,
        "todo": TODO,
        "curiosity": CURIOSITY,
        "observation": OBSERVATION,
        "command": COMMAND
    }
    return categories.get(category_name)


def get_all():
    return [
        ACTION, 
        TODO, 
        CURIOSITY, 
        OBSERVATION, 
        COMMAND
    ]
