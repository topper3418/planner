import logging
import os
from openai import OpenAI

from ..logging import get_logger
from ..config import CHAT_SERVICE

from .grok import GrokChatClient
from .openAI import OpenAIChatClient


logger = get_logger(__name__)
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
        logger.info("Using Grok")
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError("Missing API key")
        return OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
    elif CHAT_SERVICE == "openai":
        logger.info("Using OpenAI")
        return OpenAI()
    elif CHAT_SERVICE == "ollama":
        logger.info("Using Ollama")
        return OpenAI(
            base_url="http://localhost:11434/v1",  # Default Ollama local endpoint
            api_key="ollama"  # Ollama doesn't require a real API key, using dummy value
        )
    else:
        raise ValueError(f"Unsupported chat service: {CHAT_SERVICE}")
