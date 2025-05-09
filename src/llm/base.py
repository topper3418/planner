from enum import Enum

from ..logging import get_logger

logger = get_logger(__name__, "llm.log")


class Role(Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class ChatClient:
    def __init__(self):
        self._client = self._get_client()
        self.history = []
        self.system_message = None
        self.title = None

    def load_system_message(self, system_message_template: str, **kwargs):
        """
        Load the system message from a file and add it to the history.
        """
        try:
            self.system_message = system_message_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing key in system message: {e}")
        self.history.append(
            {
                "content": self.system_message,
                "role": Role.SYSTEM.value,
            }
        )

    def _get_client(self):
        pass

    def chat(self, content: str, role: str = "user") -> str:
        pass
