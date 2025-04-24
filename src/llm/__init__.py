import logging

from ..config import CHAT_SERVICE

from .grok import GrokChatClient
from .openAI import OpenAIChatClient


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_client() -> GrokChatClient | OpenAIChatClient:
    """
    Factory function to create a chat client based on the configured chat service.
    """
    if CHAT_SERVICE == "grok":
        logger.info("Using GrokChatClient")
        return GrokChatClient()
    elif CHAT_SERVICE == "openai":
        logger.info("Using OpenAIChatClient")
        return OpenAIChatClient()
    else:
        raise ValueError(f"Unsupported chat service: {CHAT_SERVICE}")
