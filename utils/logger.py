"""
Structured logging for Trader AI System.
Provides JSON-formatted logging with configurable levels and outputs.
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from config import Config


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, "run_id"):
            log_data["run_id"] = record.run_id
        
        if hasattr(record, "agent_name"):
            log_data["agent_name"] = record.agent_name
        
        if hasattr(record, "ticket"):
            log_data["ticket"] = record.ticket
        
        if hasattr(record, "confidence_score"):
            log_data["confidence_score"] = record.confidence_score
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add stack trace if present
        if record.stack_info:
            log_data["stack_trace"] = self.formatStack(record.stack_info)
        
        return json.dumps(log_data)


def setup_logging() -> None:
    """
    Configure logging for the entire application.
    Sets up both console and file handlers with JSON formatting.
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create JSON formatter
    json_formatter = JSONFormatter()
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if Config.LOG_TO_FILE:
        # Create logs directory if it doesn't exist
        log_path = Path(Config.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(Config.LOG_FILE_PATH)
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class WorkflowLogger:
    """
    Specialized logger for workflow execution with structured context.
    Provides convenience methods for logging workflow events.
    """
    
    def __init__(self, run_id: str):
        """
        Initialize workflow logger.
        
        Args:
            run_id: Unique workflow execution identifier
        """
        self.run_id = run_id
        self.logger = get_logger("workflow")
    
    def log_workflow_start(self, symbols: list[str], timeframes: list[str]) -> None:
        """Log workflow execution start."""
        self.logger.info(
            f"Workflow started: run_id={self.run_id}, symbols={symbols}, timeframes={timeframes}",
            extra={"run_id": self.run_id}
        )
    
    def log_agent_invocation(self, agent_name: str) -> None:
        """Log agent invocation."""
        self.logger.info(
            f"Agent invoked: {agent_name}",
            extra={"run_id": self.run_id, "agent_name": agent_name}
        )
    
    def log_data_collection(self, data_type: str, symbol: str, success: bool) -> None:
        """Log data collection request."""
        status = "success" if success else "failed"
        self.logger.info(
            f"Data collection {status}: type={data_type}, symbol={symbol}",
            extra={"run_id": self.run_id}
        )
    
    def log_analysis_output(self, agent_name: str, output: dict) -> None:
        """Log analysis output with reasoning."""
        self.logger.info(
            f"Analysis output from {agent_name}: {json.dumps(output)}",
            extra={"run_id": self.run_id, "agent_name": agent_name}
        )
    
    def log_strategy_decision(self, strategy_triggered: bool, direction: Optional[str], reasoning: str) -> None:
        """Log strategy decision."""
        self.logger.info(
            f"Strategy decision: triggered={strategy_triggered}, direction={direction}, reasoning={reasoning}",
            extra={"run_id": self.run_id}
        )
    
    def log_risk_assessment(self, confidence: str, confidence_score: float, reasoning: str) -> None:
        """Log risk assessment."""
        self.logger.info(
            f"Risk assessment: confidence={confidence}, score={confidence_score}, reasoning={reasoning}",
            extra={"run_id": self.run_id, "confidence_score": confidence_score}
        )
    
    def log_trade_execution(self, success: bool, ticket: Optional[int], symbol: str, 
                           volume: float, sl: float, tp: float, error: Optional[str] = None) -> None:
        """Log trade execution."""
        if success:
            self.logger.info(
                f"Trade executed: ticket={ticket}, symbol={symbol}, volume={volume}, sl={sl}, tp={tp}",
                extra={"run_id": self.run_id, "ticket": ticket}
            )
        else:
            self.logger.error(
                f"Trade execution failed: symbol={symbol}, error={error}",
                extra={"run_id": self.run_id}
            )
    
    def log_error(self, agent_name: str, error: Exception, state_snapshot: Optional[dict] = None) -> None:
        """Log error with stack trace and state snapshot."""
        self.logger.error(
            f"Error in {agent_name}: {str(error)}",
            extra={"run_id": self.run_id, "agent_name": agent_name},
            exc_info=True
        )
        
        if state_snapshot:
            self.logger.debug(
                f"State snapshot at error: {json.dumps(state_snapshot, default=str)}",
                extra={"run_id": self.run_id}
            )
    
    def log_workflow_complete(self, next_run_time: str, next_run_interval: str) -> None:
        """Log workflow completion."""
        self.logger.info(
            f"Workflow complete: next_run_time={next_run_time}, interval={next_run_interval}",
            extra={"run_id": self.run_id}
        )
