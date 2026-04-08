# Requirements Document

## Introduction

The Trader AI System is a fully autonomous multi-agent trading system that analyzes market data, evaluates trading strategies, manages risk, and executes trades on MetaTrader 5. The system uses a LangGraph-based workflow with seven specialized agents coordinated by an orchestrator, interfacing with two MCP servers for data collection (TradingView) and trade execution (MetaTrader 5). The system operates autonomously on a scheduled basis, making data-driven trading decisions while maintaining strict risk controls and optional human oversight.

## Glossary

- **Orchestrator**: The central decision-making agent that coordinates workflow and delegates tasks to specialized sub-agents
- **Data_Collector**: Agent responsible for fetching market data, news, and technical indicators via MCP 1
- **Technical_Analyst**: Agent that interprets technical indicators and price action patterns
- **News_Analyst**: Agent that analyzes news sentiment and market impact
- **Strategy_Evaluator**: Agent that determines if trading strategy conditions are met (Yes/No gate)
- **Risk_Manager**: Agent that evaluates trade confidence and calculates position sizing parameters
- **Trade_Executor**: Agent that executes trades on MetaTrader 5 via MCP 2
- **Scheduler**: Deterministic component that manages cron-based execution timing
- **MCP_1**: Model Context Protocol server providing TradingView data access
- **MCP_2**: Model Context Protocol server providing MetaTrader 5 execution access
- **TraderState**: The stateful graph context containing all workflow data
- **MT5**: MetaTrader 5 trading platform
- **OHLCV**: Open, High, Low, Close, Volume price data
- **Confidence_Score**: Numerical assessment (0.0-1.0) of trade setup quality
- **Position_Size**: Trade volume in lots calculated based on risk parameters
- **Paper_Trading**: Simulated trading mode using demo account

## Requirements

### Requirement 1: Multi-Agent Workflow Orchestration

**User Story:** As a system operator, I want the orchestrator to coordinate all agents through a defined workflow, so that trading decisions follow a consistent and auditable process.

#### Acceptance Criteria

1. THE Orchestrator SHALL coordinate agent execution through the workflow: data_collection → analysis → strategy_evaluation → risk_assessment → trade_execution
2. WHEN the workflow starts, THE Orchestrator SHALL initialize TraderState with run_id, timestamp, symbols, and timeframes
3. THE Orchestrator SHALL delegate data collection tasks to Data_Collector
4. WHEN Data_Collector completes, THE Orchestrator SHALL invoke Technical_Analyst and News_Analyst in parallel
5. WHEN both analysts complete, THE Orchestrator SHALL invoke Strategy_Evaluator
6. THE Orchestrator SHALL maintain agent_trace in TraderState recording all agent invocations
7. IF any agent returns an error, THEN THE Orchestrator SHALL record the error in TraderState.errors and continue workflow

### Requirement 2: Market Data Collection

**User Story:** As a trading system, I want to collect comprehensive market data, so that analysis agents have complete information for decision-making.

#### Acceptance Criteria

1. THE Data_Collector SHALL fetch OHLCV data for all configured symbols via MCP_1
2. THE Data_Collector SHALL fetch news data for all configured symbols via MCP_1
3. THE Data_Collector SHALL fetch technical indicator values for all configured indicators via MCP_1
4. THE Data_Collector SHALL populate TraderState.market_data with OHLCV candles
5. THE Data_Collector SHALL populate TraderState.news_data with news articles
6. THE Data_Collector SHALL populate TraderState.indicator_data with indicator values
7. IF MCP_1 returns an error for any data request, THEN THE Data_Collector SHALL record the error and continue with available data

### Requirement 3: Technical Analysis

**User Story:** As a trading system, I want to interpret technical indicators and price patterns, so that I can identify potential trading opportunities.

#### Acceptance Criteria

1. THE Technical_Analyst SHALL analyze TraderState.indicator_data and TraderState.market_data
2. THE Technical_Analyst SHALL determine trend direction as bullish, bearish, or neutral
3. THE Technical_Analyst SHALL calculate trend strength as a value between 0.0 and 1.0
4. THE Technical_Analyst SHALL identify key support and resistance levels
5. THE Technical_Analyst SHALL generate a signal of buy, sell, or hold
6. THE Technical_Analyst SHALL list all indicators used in the analysis
7. THE Technical_Analyst SHALL list all indicators that are missing or unavailable
8. THE Technical_Analyst SHALL populate TraderState.technical_analysis with structured assessment including trend, strength, key_levels, signal, indicators_used, indicators_missing, and reasoning

### Requirement 4: News Sentiment Analysis

**User Story:** As a trading system, I want to analyze news sentiment, so that I can factor fundamental events into trading decisions.

#### Acceptance Criteria

1. THE News_Analyst SHALL analyze TraderState.news_data for sentiment
2. THE News_Analyst SHALL determine sentiment as bullish, bearish, or neutral
3. THE News_Analyst SHALL assess impact_level as high, medium, or low
4. THE News_Analyst SHALL identify key_events from news articles
5. THE News_Analyst SHALL determine if news sentiment conflicts with technical analysis
6. THE News_Analyst SHALL populate TraderState.news_analysis with sentiment, impact_level, key_events, conflict_with_technical, and reasoning

### Requirement 5: Strategy Evaluation Gate

**User Story:** As a trading system, I want to determine if strategy conditions are met, so that I only proceed to risk assessment when a valid setup exists.

#### Acceptance Criteria

1. THE Strategy_Evaluator SHALL evaluate TraderState.technical_analysis and TraderState.news_analysis
2. THE Strategy_Evaluator SHALL determine if strategy_triggered is true or false
3. WHEN strategy_triggered is true, THE Strategy_Evaluator SHALL specify direction as buy or sell
4. WHEN strategy_triggered is true, THE Strategy_Evaluator SHALL specify entry_type as market or limit
5. WHEN strategy_triggered is true, THE Strategy_Evaluator SHALL provide suggested_entry price
6. THE Strategy_Evaluator SHALL populate TraderState.strategy_decision with strategy_triggered, direction, entry_type, suggested_entry, and reasoning
7. WHEN strategy_triggered is false, THE Orchestrator SHALL route workflow to Scheduler

### Requirement 6: Risk Assessment and Position Sizing

**User Story:** As a trading system, I want to evaluate trade confidence and calculate position size, so that I manage risk appropriately for each trade.

#### Acceptance Criteria

1. THE Risk_Manager SHALL evaluate TraderState.strategy_decision, TraderState.technical_analysis, and TraderState.news_analysis
2. THE Risk_Manager SHALL fetch account information via MCP_2
3. THE Risk_Manager SHALL fetch current positions via MCP_2
4. THE Risk_Manager SHALL fetch symbol specifications via MCP_2
5. THE Risk_Manager SHALL calculate confidence as high, medium, or low
6. THE Risk_Manager SHALL calculate confidence_score as a value between 0.0 and 1.0
7. WHEN confidence_score is greater than or equal to 0.75, THE Risk_Manager SHALL set confidence to high
8. WHEN confidence_score is greater than or equal to 0.50 and less than 0.75, THE Risk_Manager SHALL set confidence to medium
9. WHEN confidence_score is less than 0.50, THE Risk_Manager SHALL set confidence to low
10. THE Risk_Manager SHALL calculate risk_reward_ratio for the trade setup
11. THE Risk_Manager SHALL calculate position_size_lots based on account balance and max_risk_percent
12. THE Risk_Manager SHALL calculate stop_loss price level
13. THE Risk_Manager SHALL calculate take_profit price level
14. THE Risk_Manager SHALL reduce confidence_score when timing indicators are missing
15. THE Risk_Manager SHALL populate TraderState.risk_assessment with confidence, confidence_score, risk_reward_ratio, position_size_lots, stop_loss, take_profit, max_risk_percent, reasons_for_rejection, and reasoning
16. WHEN confidence is not high, THE Orchestrator SHALL route workflow to Scheduler

### Requirement 7: Trade Execution

**User Story:** As a trading system, I want to execute trades with exact risk parameters, so that trades are placed according to risk management decisions.

#### Acceptance Criteria

1. THE Trade_Executor SHALL execute trades only when TraderState.risk_assessment.confidence is high
2. WHEN TraderState.strategy_decision.direction is buy, THE Trade_Executor SHALL place a buy order via MCP_2
3. WHEN TraderState.strategy_decision.direction is sell, THE Trade_Executor SHALL place a sell order via MCP_2
4. THE Trade_Executor SHALL use position_size_lots from TraderState.risk_assessment
5. THE Trade_Executor SHALL use stop_loss from TraderState.risk_assessment
6. THE Trade_Executor SHALL use take_profit from TraderState.risk_assessment
7. THE Trade_Executor SHALL NOT modify risk parameters independently
8. THE Trade_Executor SHALL populate TraderState.execution_result with success status, ticket number, and error information
9. THE Trade_Executor SHALL execute at most one trade per workflow cycle

### Requirement 8: Workflow Routing Logic

**User Story:** As a trading system, I want conditional workflow routing, so that execution only occurs when strategy and risk conditions are met.

#### Acceptance Criteria

1. WHEN Strategy_Evaluator sets strategy_triggered to false, THE Orchestrator SHALL route to Scheduler
2. WHEN Strategy_Evaluator sets strategy_triggered to true, THE Orchestrator SHALL route to Risk_Manager
3. WHEN Risk_Manager sets confidence to low or medium, THE Orchestrator SHALL route to Scheduler
4. WHEN Risk_Manager sets confidence to high, THE Orchestrator SHALL route to Trade_Executor
5. WHEN Trade_Executor completes, THE Orchestrator SHALL route to Scheduler

### Requirement 9: Autonomous Scheduling

**User Story:** As a trading system, I want to schedule the next analysis cycle dynamically, so that the system adapts to market conditions and execution results.

#### Acceptance Criteria

1. THE Scheduler SHALL determine next_run_interval based on TraderState
2. WHEN a trade was just executed, THE Scheduler SHALL set next_run_interval to 5 minutes
3. WHEN strategy was triggered but confidence was low, THE Scheduler SHALL set next_run_interval to 15 minutes
4. WHEN strategy was not triggered, THE Scheduler SHALL set next_run_interval to 30 minutes
5. WHEN current time is outside market hours, THE Scheduler SHALL set next_run_time to next market open
6. THE Scheduler SHALL populate TraderState.next_run_time with the scheduled execution timestamp
7. THE Scheduler SHALL create a cron job for the next workflow execution

### Requirement 10: MCP 1 TradingView Data Interface

**User Story:** As a data collection agent, I want to access market data through MCP 1, so that I can retrieve OHLCV, news, and indicators.

#### Acceptance Criteria

1. THE MCP_1 SHALL provide tv_get_ohlcv tool accepting symbol, timeframe, and count parameters
2. THE MCP_1 SHALL provide tv_get_news tool accepting symbol and limit parameters
3. THE MCP_1 SHALL provide tv_get_indicator tool accepting symbol, timeframe, indicator_name, and params parameters
4. THE MCP_1 SHALL provide tv_get_available_indicators tool returning list of available indicators
5. THE MCP_1 SHALL provide tv_get_market_summary tool accepting symbol parameter
6. THE MCP_1 SHALL return OHLCV data as a list of candle objects
7. THE MCP_1 SHALL return news data as a list of news item objects
8. THE MCP_1 SHALL return indicator data as a dictionary with indicator values
9. THE MCP_1 SHALL provide access to 3 out of 4 timing indicators

### Requirement 11: MCP 2 MetaTrader 5 Execution Interface

**User Story:** As a trade execution agent, I want to access MT5 through MCP 2, so that I can place orders and manage positions.

#### Acceptance Criteria

1. THE MCP_2 SHALL provide mt5_initialize tool accepting login, password, server, and path parameters
2. THE MCP_2 SHALL provide mt5_get_account_info tool returning account balance, equity, and margin
3. THE MCP_2 SHALL provide mt5_get_positions tool accepting optional symbol parameter
4. THE MCP_2 SHALL provide mt5_get_orders tool accepting optional symbol parameter
5. THE MCP_2 SHALL provide mt5_buy tool accepting symbol, volume, sl, tp, comment, and magic parameters
6. THE MCP_2 SHALL provide mt5_sell tool accepting symbol, volume, sl, tp, comment, and magic parameters
7. THE MCP_2 SHALL provide mt5_close_position tool accepting ticket parameter
8. THE MCP_2 SHALL provide mt5_close_all tool accepting optional symbol parameter
9. THE MCP_2 SHALL provide mt5_modify_position tool accepting ticket, sl, and tp parameters
10. THE MCP_2 SHALL provide mt5_get_symbol_info tool accepting symbol parameter
11. THE MCP_2 SHALL provide mt5_get_ticks tool accepting symbol and count parameters
12. THE MCP_2 SHALL provide mt5_shutdown tool for connection cleanup

### Requirement 12: State Management

**User Story:** As a workflow system, I want to maintain all context in TraderState, so that agents remain stateless and the workflow is reproducible.

#### Acceptance Criteria

1. THE TraderState SHALL contain symbols as a list of trading symbols
2. THE TraderState SHALL contain timeframes as a list of analysis timeframes
3. THE TraderState SHALL contain run_id as a unique workflow execution identifier
4. THE TraderState SHALL contain timestamp as the workflow start time
5. THE TraderState SHALL contain market_data as a dictionary of OHLCV data
6. THE TraderState SHALL contain news_data as a list of news articles
7. THE TraderState SHALL contain indicator_data as a dictionary of indicator values
8. THE TraderState SHALL contain technical_analysis as a dictionary of technical assessment
9. THE TraderState SHALL contain news_analysis as a dictionary of sentiment assessment
10. THE TraderState SHALL contain strategy_decision as a dictionary of strategy evaluation
11. THE TraderState SHALL contain risk_assessment as a dictionary of risk parameters
12. THE TraderState SHALL contain execution_result as a dictionary of trade execution outcome
13. THE TraderState SHALL contain next_run_time as the scheduled next execution
14. THE TraderState SHALL contain next_run_interval as the interval until next execution
15. THE TraderState SHALL contain agent_trace as an append-only list of agent invocations
16. THE TraderState SHALL contain errors as an append-only list of error messages

### Requirement 13: Paper Trading Mode

**User Story:** As a system operator, I want to run the system in paper trading mode, so that I can validate strategies without risking real capital.

#### Acceptance Criteria

1. WHERE paper trading mode is enabled, THE MCP_2 SHALL connect to a demo MT5 account
2. WHERE paper trading mode is enabled, THE Trade_Executor SHALL execute all trades on the demo account
3. WHERE paper trading mode is enabled, THE System SHALL log all trades with a paper trading indicator
4. THE System SHALL support configuration to enable or disable paper trading mode

### Requirement 14: Human-in-the-Loop Override

**User Story:** As a system operator, I want optional human approval before trade execution, so that I can maintain oversight during initial deployment.

#### Acceptance Criteria

1. WHERE human-in-the-loop is enabled, THE Orchestrator SHALL pause workflow before Trade_Executor
2. WHERE human-in-the-loop is enabled, THE System SHALL wait for human approval or rejection
3. WHEN human approves, THE Orchestrator SHALL proceed to Trade_Executor
4. WHEN human rejects, THE Orchestrator SHALL route to Scheduler
5. THE System SHALL support configuration to enable or disable human-in-the-loop

### Requirement 15: Error Handling and Recovery

**User Story:** As a trading system, I want to handle errors gracefully, so that temporary failures do not crash the system.

#### Acceptance Criteria

1. WHEN any agent encounters an error, THE Agent SHALL record the error in TraderState.errors
2. WHEN MCP_1 connection fails, THE Data_Collector SHALL retry up to 3 times with exponential backoff
3. WHEN MCP_2 connection fails, THE Trade_Executor SHALL record the error and skip execution
4. WHEN an agent times out, THE Orchestrator SHALL record the timeout and continue workflow
5. IF critical errors prevent workflow completion, THEN THE Orchestrator SHALL route to Scheduler with extended interval
6. THE System SHALL log all errors with timestamp, agent name, and error details

### Requirement 16: Logging and Audit Trail

**User Story:** As a system operator, I want comprehensive logging, so that I can audit all trading decisions and troubleshoot issues.

#### Acceptance Criteria

1. THE System SHALL log each workflow execution with run_id and timestamp
2. THE System SHALL log all agent invocations in agent_trace
3. THE System SHALL log all data collection requests and responses
4. THE System SHALL log all analysis outputs with reasoning
5. THE System SHALL log all strategy decisions with reasoning
6. THE System SHALL log all risk assessments with confidence scores
7. THE System SHALL log all trade executions with ticket numbers and parameters
8. THE System SHALL log all errors with stack traces
9. THE System SHALL support configurable log levels: DEBUG, INFO, WARNING, ERROR
10. THE System SHALL support logging to file and console

### Requirement 17: Configuration Management

**User Story:** As a system operator, I want to configure system parameters, so that I can adapt the system to different trading strategies and risk profiles.

#### Acceptance Criteria

1. THE System SHALL load configuration from environment variables
2. THE System SHALL support configuration of symbols to trade
3. THE System SHALL support configuration of timeframes to analyze
4. THE System SHALL support configuration of max_risk_per_trade_pct
5. THE System SHALL support configuration of default_risk_reward_ratio
6. THE System SHALL support configuration of confidence_threshold
7. THE System SHALL support configuration of default_analysis_interval
8. THE System SHALL support configuration of market_open_hour and market_close_hour
9. THE System SHALL support configuration of LLM API keys for OpenAI or Anthropic
10. THE System SHALL support configuration of MT5 connection parameters
11. THE System SHALL validate all configuration values at startup

### Requirement 18: Single Trade Per Cycle Constraint

**User Story:** As a risk management system, I want to limit execution to one trade per cycle, so that I prevent overtrading and maintain capital preservation.

#### Acceptance Criteria

1. THE Trade_Executor SHALL execute at most one trade per workflow cycle
2. WHEN Trade_Executor places a trade, THE Trade_Executor SHALL mark the cycle as executed
3. IF a trade was already executed in the current cycle, THEN THE Trade_Executor SHALL skip additional execution requests
4. THE System SHALL reset the execution flag at the start of each new workflow cycle

### Requirement 19: Missing Indicator Awareness

**User Story:** As a risk management system, I want to account for missing indicators, so that confidence scores reflect data completeness.

#### Acceptance Criteria

1. THE Technical_Analyst SHALL identify which timing indicators are missing
2. THE Technical_Analyst SHALL record missing indicators in TraderState.technical_analysis.indicators_missing
3. THE Risk_Manager SHALL reduce confidence_score when indicators are missing
4. WHEN 1 timing indicator is missing, THE Risk_Manager SHALL reduce confidence_score by 0.10
5. THE Risk_Manager SHALL include missing indicators in reasoning for confidence assessment

### Requirement 20: Agent LLM Configuration

**User Story:** As a system architect, I want agents to use appropriate LLM models, so that I balance reasoning capability with cost and latency.

#### Acceptance Criteria

1. THE Orchestrator SHALL use GPT-4o or Claude 3.5 Sonnet
2. THE Data_Collector SHALL use GPT-4o-mini
3. THE Technical_Analyst SHALL use GPT-4o
4. THE News_Analyst SHALL use GPT-4o
5. THE Strategy_Evaluator SHALL use GPT-4o
6. THE Risk_Manager SHALL use GPT-4o
7. THE Trade_Executor SHALL use GPT-4o-mini
8. THE Scheduler SHALL NOT use an LLM
9. THE System SHALL support configuration to override default LLM models per agent
