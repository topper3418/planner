from enum import Enum
import os

from openai import OpenAI


class Role(Enum):
    SYSTEM = 'system'
    ASSISTANT = 'assistant'
    USER = 'user'


class ChatClient: 
    def __init__(self):
        self._client = self._get_client()
        self.history = []

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

    def chat(self, content: str, role: str = 'user') -> str:
        self.history.append({
            "content": content,
            "role": role,
        })
        response = self._client.chat.completions.create(
            model="grok-2-latest",
            messages=self.history,
            response_format={ "type": "json_object" }
        )
        message = response.choices[0].message
        self.history.append(message)
        return message.content


def get_client():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("Missing API key")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1"
    )

