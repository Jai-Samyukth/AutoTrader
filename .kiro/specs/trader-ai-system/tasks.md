# Implementation Plan: Trader AI System

## Overview

This implementation plan breaks down the Trader AI System into discrete coding tasks. The system is a fully autonomous multi-agent trading platform using LangGraph for workflow orchestration, with 7 specialized agents coordinated by an orchestrator. The implementation follows a bottom-up approach: infrastructure → data models → MCP servers → agents → workflow → testing.

## Tasks

- [x] 1. Set up project infrastructure and configuration
  - Create project directory structure (graph/, agents/, mcp_servers/, prompts/, utils/, tests/)
  - Set up pyproject.toml with dependencies (langgraph, langchain, pydantic, MetaTrader5, yfinance, APScheduler, hypothesis)
  - Create config.py to load environment variables and validate configuration
  - Create utils/logger.py for structured logging with JSON format
  - _Requirements: 17.1, 17.2, 17.11, 16.9, 16.10_

- [-] 2. Implement core data models and state management
  - [-] 2.1 Create TraderState TypedDict in graph/state.py
    - Define all state fields: symbols, timeframes, run_id, timestamp, market_data, news_data, indicator_data, technical_analysis, news_analysis, strategy_decision, risk_assessment, execution_result, next_run_time, next_run_interval, agent_trace, errors
    - Use Annotated with operator.add for agent_trace and errors
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10, 12.11, 12.12, 12.13, 12.14, 12.15, 12.16_

  - [ ]* 2.2 Write property test for TraderState schema completeness
    - **Property 26: TraderState Schema Completeness**
    - **Validates: Requirements 12.1-12.16**

  - [ ] 2.3 Create MT5 data models in mcp_servers/mt5_server/models.py
    - Define OrderType enum, AccountInfo, Position, OrderRequest, ExecutionResult, SymbolInfo Pydantic models
    - _Requirements: 11.2, 11.3, 11.4, 11.5, 11.6, 11.10_

  - [ ] 2.4 Create TradingView data models in mcp_servers/tradingview_server/models.py
    - Define Candle, NewsItem, IndicatorData, MarketSummary Pydantic models
    - _Requirements: 10.6, 10.7, 10.8_

- [ ] 3. Implement MCP 2 - MetaTrader 5 Execution Server
  - [ ] 3.1 Create MT5Wrapper singleton class in mcp_servers/mt5_server/mt5_wrapper.py
    - Implement initialize(), shutdown(), is_connected property
    - Implement get_account_info(), get_positions(), get_orders()
    - Implement buy(), sell(), close_position(), close_all(), modify_position()
    - Implement get_symbol_info(), get_ticks()
    - Implement place_limit_order(), cancel_order()
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 11.10, 11.11, 11.12_

  - [ ]* 3.2 Write unit tests for MT5Wrapper
    - Test connection lifecycle (initialize, shutdown)
    - Test order execution (buy, sell, close)
    - Test error handling for connection failures
    - _Requirements: 11.1, 11.5, 11.6, 11.7_

  - [ ] 3.3 Create MCP 2 server tools in mcp_servers/mt5_server/tools.py
    - Define tool functions wrapping MT5Wrapper methods
    - Add tool descriptions and parameter schemas
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 11.10, 11.11, 11.12_

  - [ ] 3.4 Create MCP 2 server entry point in mcp_servers/mt5_server/server.py
    - Initialize MCP server with all tools
    - Handle server lifecycle
    - _Requirements: 11.1, 11.12_

- [ ] 4. Implement MCP 1 - TradingView Data Server
  - [ ] 4.1 Create TradingViewWrapper class in mcp_servers/tradingview_server/tv_wrapper.py
    - Implement get_ohlcv() using yfinance
    - Implement get_news() using news API
    - Implement get_indicator() for RSI, MACD, EMA, SMA, Bollinger Bands, ATR, ADX, Stochastic
    - Implement get_available_indicators() returning 3 of 4 timing indicators
    - Implement get_market_summary()
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.9_

  - [ ]* 4.2 Write unit tests for TradingViewWrapper
    - Test OHLCV data fetching
    - Test indicator calculations
    - Test error handling for API failures
    - _Requirements: 10.1, 10.3, 2.7_

  - [ ]* 4.3 Write property test for MCP_1 response formats
    - **Property 23: MCP_1 OHLCV Response Format**
    - **Property 24: MCP_1 News Response Format**
    - **Property 25: MCP_1 Indicator Response Format**
    - **Validates: Requirements 10.6, 10.7, 10.8**

  - [ ] 4.4 Create MCP 1 server tools in mcp_servers/tradingview_server/tools.py
    - Define tool functions wrapping TradingViewWrapper methods
    - Add tool descriptions and parameter schemas
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 4.5 Create MCP 1 server entry point in mcp_servers/tradingview_server/server.py
    - Initialize MCP server with all tools
    - Handle server lifecycle
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 5. Checkpoint - Ensure MCP servers are functional
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement Data Collector Agent
  - [ ] 6.1 Create Data_Collector agent in agents/data_collector.py
    - Create LangChain tool-calling agent with GPT-4o-mini
    - Bind all MCP 1 tools
    - Implement data collection logic to populate market_data, news_data, indicator_data
    - Implement error handling to continue with available data on MCP_1 failures
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 6.2 Write property test for data collection completeness
    - **Property 4: Data Collection Completeness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

  - [ ]* 6.3 Write property test for data collection error resilience
    - **Property 5: Data Collection Error Resilience**
    - **Validates: Requirements 2.7**

  - [ ]* 6.4 Write property test for MCP_1 connection retry
    - **Property 30: MCP_1 Connection Retry**
    - **Validates: Requirements 15.2**

- [ ] 7. Implement Technical Analyst Agent
  - [ ] 7.1 Create Technical_Analyst agent in agents/technical_analyst.py
    - Create LangChain tool-calling agent with GPT-4o
    - Bind tv_get_indicator and tv_get_ohlcv tools
    - Create prompt in prompts/technical_analyst.md for indicator interpretation
    - Implement analysis logic to populate technical_analysis with trend, strength, key_levels, signal, indicators_used, indicators_missing, reasoning
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [ ]* 7.2 Write property test for technical analysis output schema
    - **Property 6: Technical Analysis Output Schema**
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8**

  - [ ]* 7.3 Write unit tests for Technical_Analyst
    - Test trend detection with sample indicator data
    - Test missing indicator tracking
    - _Requirements: 3.2, 3.7, 19.1_

- [ ] 8. Implement News Analyst Agent
  - [ ] 8.1 Create News_Analyst agent in agents/news_analyst.py
    - Create LangChain tool-calling agent with GPT-4o
    - Bind tv_get_news tool
    - Create prompt in prompts/news_analyst.md for sentiment analysis
    - Implement analysis logic to populate news_analysis with sentiment, impact_level, key_events, conflict_with_technical, reasoning
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]* 8.2 Write property test for news analysis output schema
    - **Property 7: News Analysis Output Schema**
    - **Validates: Requirements 4.2, 4.3, 4.4, 4.5, 4.6**

  - [ ]* 8.3 Write unit tests for News_Analyst
    - Test sentiment classification with sample news data
    - Test conflict detection with technical analysis
    - _Requirements: 4.2, 4.5_

- [ ] 9. Implement Strategy Evaluator Agent
  - [ ] 9.1 Create Strategy_Evaluator agent in agents/strategy_evaluator.py
    - Create LangChain tool-calling agent with GPT-4o (no external tools)
    - Create prompt in prompts/strategy_evaluator.md for strategy evaluation
    - Implement evaluation logic to populate strategy_decision with strategy_triggered, direction, entry_type, suggested_entry, reasoning
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ]* 9.2 Write property test for strategy decision output schema
    - **Property 8: Strategy Decision Output Schema**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6**

  - [ ]* 9.3 Write unit tests for Strategy_Evaluator
    - Test strategy triggering with bullish technical + bullish news
    - Test strategy rejection with conflicting signals
    - _Requirements: 5.2, 5.6_

- [ ] 10. Implement Risk Manager Agent
  - [ ] 10.1 Create Risk_Manager agent in agents/risk_manager.py
    - Create LangChain tool-calling agent with GPT-4o
    - Bind mt5_get_account_info, mt5_get_positions, mt5_get_symbol_info tools
    - Create prompt in prompts/risk_manager.md for risk assessment
    - Implement confidence scoring logic with thresholds (high >= 0.75, medium >= 0.50, low < 0.50)
    - Implement missing indicator penalty (reduce confidence_score by 0.10 per missing indicator)
    - Implement position sizing calculation based on account balance and max_risk_percent
    - Implement stop_loss and take_profit calculation
    - Populate risk_assessment with confidence, confidence_score, risk_reward_ratio, position_size_lots, stop_loss, take_profit, max_risk_percent, reasons_for_rejection, reasoning
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12, 6.13, 6.14, 6.15_

  - [ ]* 10.2 Write property test for risk assessment output schema
    - **Property 9: Risk Assessment Output Schema**
    - **Validates: Requirements 6.5, 6.6, 6.10, 6.11, 6.12, 6.13, 6.15**

  - [ ]* 10.3 Write property test for confidence score to level mapping
    - **Property 10: Confidence Score to Confidence Level Mapping**
    - **Validates: Requirements 6.7, 6.8, 6.9**

  - [ ]* 10.4 Write property test for missing indicator confidence penalty
    - **Property 11: Missing Indicator Confidence Penalty**
    - **Validates: Requirements 6.14, 19.3, 19.4, 19.5**

  - [ ]* 10.5 Write unit tests for Risk_Manager
    - Test position sizing calculation with various account balances
    - Test stop_loss and take_profit calculation
    - Test confidence reduction with missing indicators
    - _Requirements: 6.11, 6.12, 6.13, 6.14_

- [ ] 11. Implement Trade Executor Agent
  - [ ] 11.1 Create Trade_Executor agent in agents/trade_executor.py
    - Create LangChain tool-calling agent with GPT-4o-mini
    - Bind all MCP 2 tools
    - Create prompt in prompts/trade_executor.md emphasizing exact parameter usage
    - Implement execution logic to place buy/sell orders using exact risk_assessment parameters
    - Implement single trade per cycle constraint with execution flag
    - Populate execution_result with success, ticket, error
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 18.1, 18.2, 18.3_

  - [ ]* 11.2 Write property test for trade execution confidence gate
    - **Property 12: Trade Execution Confidence Gate**
    - **Validates: Requirements 7.1**

  - [ ]* 11.3 Write property test for trade direction correctness
    - **Property 13: Trade Direction Correctness**
    - **Validates: Requirements 7.2, 7.3**

  - [ ]* 11.4 Write property test for trade parameter fidelity
    - **Property 14: Trade Parameter Fidelity**
    - **Validates: Requirements 7.4, 7.5, 7.6, 7.7**

  - [ ]* 11.5 Write property test for execution result completeness
    - **Property 15: Execution Result Completeness**
    - **Validates: Requirements 7.8**

  - [ ]* 11.6 Write property test for single trade per cycle constraint
    - **Property 16: Single Trade Per Cycle Constraint**
    - **Validates: Requirements 7.9, 18.1, 18.2, 18.3**

  - [ ]* 11.7 Write property test for execution flag reset
    - **Property 17: Execution Flag Reset**
    - **Validates: Requirements 18.4**

  - [ ]* 11.8 Write property test for MCP_2 connection failure handling
    - **Property 31: MCP_2 Connection Failure Handling**
    - **Validates: Requirements 15.3**

  - [ ]* 11.9 Write unit tests for Trade_Executor
    - Test buy order execution with mock MT5
    - Test sell order execution with mock MT5
    - Test execution skipping when confidence is not high
    - Test single trade per cycle enforcement
    - _Requirements: 7.2, 7.3, 7.1, 7.9_

- [ ] 12. Implement Scheduler Component
  - [ ] 12.1 Create Scheduler in agents/scheduler.py
    - Implement deterministic scheduling logic (no LLM)
    - Implement dynamic interval calculation: 5 min after trade, 15 min after low confidence, 30 min after no strategy
    - Implement market hours checking and next market open calculation
    - Populate next_run_time and next_run_interval in TraderState
    - Integrate with APScheduler for cron job creation
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [ ]* 12.2 Write property test for dynamic scheduling based on execution
    - **Property 18: Dynamic Scheduling Based on Execution**
    - **Validates: Requirements 9.2**

  - [ ]* 12.3 Write property test for dynamic scheduling based on low confidence
    - **Property 19: Dynamic Scheduling Based on Low Confidence**
    - **Validates: Requirements 9.3**

  - [ ]* 12.4 Write property test for dynamic scheduling based on no strategy
    - **Property 20: Dynamic Scheduling Based on No Strategy**
    - **Validates: Requirements 9.4**

  - [ ]* 12.5 Write property test for market hours scheduling
    - **Property 21: Market Hours Scheduling**
    - **Validates: Requirements 9.5**

  - [ ]* 12.6 Write property test for scheduler output completeness
    - **Property 22: Scheduler Output Completeness**
    - **Validates: Requirements 9.1, 9.6**

  - [ ]* 12.7 Write unit tests for Scheduler
    - Test interval calculation for each scenario
    - Test market hours detection
    - Test next market open calculation
    - _Requirements: 9.2, 9.3, 9.4, 9.5_

- [ ] 13. Checkpoint - Ensure all agents are functional
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Implement LangGraph workflow orchestration
  - [ ] 14.1 Create workflow routing functions in graph/routers.py
    - Implement route_strategy() to check strategy_triggered
    - Implement route_risk() to check confidence level
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ] 14.2 Create agent node functions in graph/nodes.py
    - Create orchestrator_node() to initialize workflow and coordinate agents
    - Create data_collector_node() wrapping Data_Collector agent
    - Create technical_analyst_node() wrapping Technical_Analyst agent
    - Create news_analyst_node() wrapping News_Analyst agent
    - Create strategy_evaluator_node() wrapping Strategy_Evaluator agent
    - Create risk_manager_node() wrapping Risk_Manager agent
    - Create trade_executor_node() wrapping Trade_Executor agent
    - Create scheduler_node() wrapping Scheduler component
    - Add agent_trace logging to each node
    - Add error handling to record errors and continue workflow
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [ ] 14.3 Create LangGraph StateGraph in graph/workflow.py
    - Build StateGraph with TraderState
    - Add all agent nodes
    - Set orchestrator as entry point
    - Add edges: orchestrator → data_collector → (technical_analyst, news_analyst) → strategy_evaluator
    - Add conditional edge from strategy_evaluator using route_strategy
    - Add conditional edge from risk_manager using route_risk
    - Add edge: trade_executor → scheduler → END
    - Compile graph
    - _Requirements: 1.1, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ]* 14.4 Write property test for workflow initialization completeness
    - **Property 1: Workflow Initialization Completeness**
    - **Validates: Requirements 1.2**

  - [ ]* 14.5 Write property test for agent trace completeness
    - **Property 2: Agent Trace Completeness**
    - **Validates: Requirements 1.6**

  - [ ]* 14.6 Write property test for error recording and continuation
    - **Property 3: Error Recording and Continuation**
    - **Validates: Requirements 1.7, 15.1**

  - [ ]* 14.7 Write property test for agent timeout handling
    - **Property 32: Agent Timeout Handling**
    - **Validates: Requirements 15.4**

  - [ ]* 14.8 Write property test for critical error recovery
    - **Property 33: Critical Error Recovery**
    - **Validates: Requirements 15.5**

- [ ] 15. Implement Orchestrator Agent
  - [ ] 15.1 Create Orchestrator agent in agents/orchestrator.py
    - Create LangChain agent with GPT-4o or Claude 3.5 Sonnet
    - Create prompt in prompts/orchestrator.md for workflow coordination
    - Implement workflow initialization with run_id and timestamp generation
    - Implement agent delegation logic
    - Implement error handling to record errors and continue workflow
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 1.7_

  - [ ]* 15.2 Write unit tests for Orchestrator
    - Test workflow initialization
    - Test agent delegation
    - Test error handling
    - _Requirements: 1.2, 1.3, 1.7_

- [ ] 16. Implement configuration management and validation
  - [ ] 16.1 Enhance config.py with configuration validation
    - Load all environment variables: symbols, timeframes, max_risk_per_trade_pct, default_risk_reward_ratio, confidence_threshold, default_analysis_interval, market_open_hour, market_close_hour, LLM API keys, MT5 connection parameters
    - Validate all configuration values at startup
    - Raise errors for missing or invalid configuration
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9, 17.10, 17.11_

  - [ ]* 16.2 Write property test for configuration validation
    - **Property 36: Configuration Validation**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8, 17.9, 17.10, 17.11**

  - [ ]* 16.3 Write unit tests for config.py
    - Test configuration loading from environment variables
    - Test validation errors for missing configuration
    - Test validation errors for invalid configuration values
    - _Requirements: 17.1, 17.11_

- [ ] 17. Implement logging and audit trail
  - [ ] 17.1 Enhance utils/logger.py with comprehensive logging
    - Implement structured JSON logging
    - Log workflow execution with run_id and timestamp
    - Log all agent invocations
    - Log all data collection requests and responses
    - Log all analysis outputs with reasoning
    - Log all strategy decisions with reasoning
    - Log all risk assessments with confidence scores
    - Log all trade executions with ticket numbers and parameters
    - Log all errors with stack traces and TraderState snapshot
    - Support configurable log levels (DEBUG, INFO, WARNING, ERROR)
    - Support logging to file and console
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 16.10_

  - [ ]* 17.2 Write property test for error logging completeness
    - **Property 34: Error Logging Completeness**
    - **Validates: Requirements 15.6, 16.8**

  - [ ]* 17.3 Write property test for workflow logging completeness
    - **Property 35: Workflow Logging Completeness**
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8**

  - [ ]* 17.4 Write unit tests for logger
    - Test JSON log formatting
    - Test log level filtering
    - Test file and console output
    - _Requirements: 16.9, 16.10_

- [ ] 18. Implement paper trading mode
  - [ ] 18.1 Add paper trading configuration to config.py
    - Add PAPER_TRADING_MODE environment variable
    - Add MT5_DEMO_ACCOUNT configuration
    - _Requirements: 13.4_

  - [ ] 18.2 Modify MT5Wrapper to support paper trading mode
    - Connect to demo account when paper trading mode is enabled
    - Add paper trading indicator to all trade logs
    - _Requirements: 13.1, 13.2, 13.3_

  - [ ]* 18.3 Write property test for paper trading mode connection
    - **Property 27: Paper Trading Mode Connection**
    - **Validates: Requirements 13.1, 13.2, 13.3**

  - [ ]* 18.4 Write unit tests for paper trading mode
    - Test demo account connection
    - Test paper trading log indicator
    - _Requirements: 13.1, 13.3_

- [ ] 19. Implement human-in-the-loop override
  - [ ] 19.1 Add human-in-the-loop configuration to config.py
    - Add HUMAN_IN_THE_LOOP environment variable
    - _Requirements: 14.5_

  - [ ] 19.2 Modify graph/workflow.py to support human-in-the-loop
    - Add interrupt_before=["trade_executor"] when human-in-the-loop is enabled
    - Implement approval/rejection routing
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

  - [ ]* 19.3 Write property test for human-in-the-loop pause
    - **Property 28: Human-in-the-Loop Pause**
    - **Validates: Requirements 14.1**

  - [ ]* 19.4 Write property test for human-in-the-loop routing
    - **Property 29: Human-in-the-Loop Routing**
    - **Validates: Requirements 14.3, 14.4**

  - [ ]* 19.5 Write unit tests for human-in-the-loop
    - Test workflow pause before trade execution
    - Test approval routing to trade executor
    - Test rejection routing to scheduler
    - _Requirements: 14.1, 14.3, 14.4_

- [ ] 20. Create main entry point and wire everything together
  - [ ] 20.1 Create main.py entry point
    - Load configuration from config.py
    - Initialize MCP servers
    - Build LangGraph workflow
    - Initialize APScheduler with Scheduler component
    - Start initial workflow execution
    - Handle graceful shutdown
    - _Requirements: 1.1, 9.7, 17.11_

  - [ ]* 20.2 Write integration tests for end-to-end workflow
    - Test complete workflow path: data collection → analysis → strategy triggered → high confidence → execution
    - Test workflow path: data collection → analysis → strategy not triggered → scheduler
    - Test workflow path: data collection → analysis → strategy triggered → low confidence → scheduler
    - Test error recovery and workflow continuation
    - _Requirements: 1.1, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 21. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify all 36 correctness properties pass with minimum 100 iterations
  - Ensure test coverage meets requirements (MCP servers 90%+, agents 85%+, workflow routing 100%, error handling 90%+)
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- Checkpoints ensure incremental validation
- The implementation follows a bottom-up approach: infrastructure → data models → MCP servers → agents → workflow → integration
- All agents use LangChain's create_tool_calling_agent pattern
- The Orchestrator coordinates workflow through LangGraph StateGraph
- The Scheduler uses deterministic logic without LLM
- Paper trading mode and human-in-the-loop are optional features configured via environment variables
