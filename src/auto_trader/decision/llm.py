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
        
        # Check if using custom base URL (e.g., OpenRouter)
        if config.llm_base_url:
            logger.info(f"Using custom base URL: {config.llm_base_url}")
            return ChatOpenAI(
                model=config.llm_model,
                temperature=config.llm_temperature,
                api_key=config.openai_api_key,
                base_url=config.llm_base_url,
            )
        else:
            return ChatOpenAI(
                model=config.llm_model,
                temperature=config.llm_temperature,
                api_key=config.openai_api_key,
            )

    elif config.is_groq:
        if not config.llm_api_key:
            raise ValueError("LLM_API_KEY not set for GROQ")
        if not config.llm_base_url:
            raise ValueError("LLM_BASE_URL not set for GROQ")

        logger.info(f"Initializing GROQ LLM: {config.llm_model}")
        return ChatOpenAI(
            model=config.llm_model,
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
            temperature=config.llm_temperature,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {config.llm_provider}")


def create_structured_llm(output_schema: type) -> BaseChatModel:
    """Create LLM with structured output."""
    llm = get_llm()
    return llm.with_structured_output(output_schema)
