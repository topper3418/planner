import logging
import os
from openai import OpenAI

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


def get_light_client() -> OpenAI:
    """
    Factory function to create a light client based on the configured chat service.
    """
    if CHAT_SERVICE == "grok":
        logger.info("Using GrokChatClient")
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError("Missing API key")
        return OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
    elif CHAT_SERVICE == "openai":
        logger.info("Using OpenAIChatClient")
        return OpenAI()
    else:
        raise ValueError(f"Unsupported chat service: {CHAT_SERVICE}")
