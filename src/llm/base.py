from enum import Enum

from ..logging import get_logger

logger = get_logger(__name__, 'llm.log')

class Role(Enum):
    SYSTEM = 'system'
    ASSISTANT = 'assistant'
    USER = 'user'


class ChatClient: 
    def __init__(self):
        self._client = self._get_client()
        self.history = []
        self.system_message = None
        self.title = None

    def load_system_message(self, system_message_filename: str, **kwargs):
        """
        Load the system message from a file and add it to the history.
        """
        if not system_message_filename.endswith('.txt'):
            system_message_filename += '.txt'
        system_message_filepath = 'src/system_messages/' + system_message_filename
        with open(system_message_filepath, 'r') as f:
            system_message = f.read()
            logger.debug('system message template loaded:\n' + system_message)
        try:
            logger.info(f'loading system template "{system_message_filename}", kwargs are:\n' + str(kwargs))
            self.system_message = system_message.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing key in system message: {e}")
        self.title = system_message_filename
        self.history.append({
            "content": self.system_message,
            "role": Role.SYSTEM.value,
        })

    def _get_client(self):
        pass

    def chat(self, content: str, role: str = 'user') -> str:
        pass
