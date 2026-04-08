# Trader AI System - Setup Guide

## Project Structure

The project has been initialized with the following structure:

```
trader-ai-system/
├── agents/                         # Agent implementations
├── graph/                          # LangGraph workflow components
├── mcp_servers/                    # MCP server implementations
│   ├── mt5_server/                # MetaTrader 5 execution server
│   └── tradingview_server/        # TradingView data server
├── prompts/                        # Agent prompt templates
├── utils/                          # Utility modules
│   └── logger.py                  # Structured JSON logging
├── tests/                          # Test suite
├── config.py                       # Configuration management
├── main.py                         # Application entry point
├── pyproject.toml                  # Project dependencies
└── .env.example                    # Environment variable template

```

## Installation

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

3. **Required environment variables:**
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - LLM provider API key
   - `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER` - MetaTrader 5 credentials
   - `SYMBOLS` - Trading symbols (comma-separated)
   - `TIMEFRAMES` - Analysis timeframes (comma-separated)

## Configuration

The `config.py` module handles all configuration management:

- **Loads environment variables** from `.env` file
- **Validates all required settings** at startup
- **Provides type-safe access** to configuration values
- **Raises ConfigurationError** if required values are missing

## Logging

The `utils/logger.py` module provides structured JSON logging:

- **JSON format** for easy parsing and analysis
- **Configurable log levels** (DEBUG, INFO, WARNING, ERROR)
- **Console and file output** support
- **Workflow-specific logger** with run_id tracking
- **Automatic error logging** with stack traces

## Next Steps

Proceed with implementing the remaining tasks:
- Task 2: Core data models and state management
- Task 3: MCP 2 - MetaTrader 5 Execution Server
- Task 4: MCP 1 - TradingView Data Server
- And so on...

Refer to `.kiro/specs/trader-ai-system/tasks.md` for the complete implementation plan.
