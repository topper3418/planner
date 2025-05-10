import json
import os
from pprint import pformat

from openai import OpenAI

from ..logging import get_logger

from .base import ChatClient


logger = get_logger(__name__, 'llm.log')


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

        initial_retries = retries

        while retries > 0:
            try:
                print("CHATTING WITH HISTORY-----------------------------")
                from pprint import pprint
                pprint(self.history)
                logger.debug(f'client "{self.title}" chatting with history:\n' + str(self.history))
                response = self._client.chat.completions.create(
                    model="grok-2-latest",
                    messages=self.history,
                    response_format={"type": "json_object"}
                )
                message = response.choices[0].message
                self.history.append(message)
                # Parse the response to ensure it’s valid JSON
                try:
                    response_obj = json.loads(message.content.strip())
                    logger.info(f'Chat response for "{self.title}":\n{pformat(response_obj)}')
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
        logger.error(f"Failed to get valid response after {initial_retries} retries")
        raise ValueError(f"Failed to get a valid response from the chat client after {initial_retries} retries")


