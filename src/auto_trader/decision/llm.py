"""LLM initialization and configuration."""

import logging

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from auto_trader.config import config

logger = logging.getLogger(__name__)


def get_llm() -> BaseChatModel:
    """Get configured LLM instance."""
    if config.is_anthropic:
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        logger.info(f"Initializing Anthropic LLM: {config.llm_model}")
        return ChatAnthropic(
            model=config.llm_model,
            temperature=config.llm_temperature,
            api_key=config.anthropic_api_key,
        )

    elif config.is_openai:
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set")

        logger.info(f"Initializing OpenAI LLM: {config.llm_model}")
        return ChatOpenAI(
            model=config.llm_model,
            temperature=config.llm_temperature,
            api_key=config.openai_api_key,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")


def create_structured_llm(output_schema: type) -> BaseChatModel:
    """Create LLM with structured output."""
    llm = get_llm()
    return llm.with_structured_output(output_schema)
