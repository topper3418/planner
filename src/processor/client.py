import logging
import json
from enum import Enum
import os
from pprint import pformat

from openai import OpenAI

logger = logging.getLogger(__name__)


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
        system_message_filepath = 'src/processor/system_messages/' + system_message_filename
        with open(system_message_filepath, 'r') as f:
            system_message = f.read()
            logger.debug('system message template loaded:\n' + system_message)
        try:
            logger.debug('kwargs are:\n' + str(kwargs))
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


class GrokChatClient(ChatClient):
    def _get_client(self) -> OpenAI:
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError("Missing API key")
        return OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )

    def chat(self, content: str, role: str = 'user', retries: int = 3) -> dict:
        """
        Send a message to the chat client and return the response content.
        Retries on failure up to the specified number of retries.
        """
        self.history.append({
            "content": content,
            "role": role,
        })

        while retries > 0:
            try:
                response = self._client.chat.completions.create(
                    model="grok-2-latest",
                    messages=self.history,
                    response_format={"type": "json_object"}
                )
                message = response.choices[0].message
                self.history.append(message)
                logger.debug(f'client "{self.title}" chatting with history:\n' + str(self.history))
                # Parse the response to ensure it’s valid JSON
                try:
                    response_obj = json.loads(message.content.strip())
                    logger.debug(f'Chat response for "{self.title}":\n{pformat(response_obj)}')
                    return response_obj
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse response: {message.content}")
                    retries -= 1
                    self.history.append({
                        "content": f"your response produced the following error:\n{str(e)}",
                        "role": "user",
                    })
                    continue
            except Exception as e:
                logger.error(f"Unexpected error during chat: {e}")
                retries -= 1
                self.history.append({
                    "content": f"your response produced the following unexpected error:\n{str(e)}",
                    "role": "user",
                })
                continue
        
        # If all retries fail
        logger.error(f"Failed to get valid response after {retries} retries")
        raise ValueError("Failed to get a valid response from the chat client after retries")


