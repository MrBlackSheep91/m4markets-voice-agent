"""
Advanced Logging Configuration for M4Markets Voice Agent
Provides persistent logging with rotation, structured logs, and multiple handlers
"""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields if present
        if hasattr(record, "call_id"):
            log_data["call_id"] = record.call_id
        if hasattr(record, "lead_phone"):
            log_data["lead_phone"] = record.lead_phone
        if hasattr(record, "duration"):
            log_data["duration_seconds"] = record.duration

        return json.dumps(log_data)


class SimpleFormatter(logging.Formatter):
    """Human-readable formatter for console output"""

    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def setup_logger(
    name="m4markets-agent",
    log_level=None,
    log_dir="logs",
    enable_console=True,
    enable_file=True,
    enable_json=True
):
    """
    Setup comprehensive logging for the application

    Args:
        name: Logger name
        log_level: Logging level (defaults to env LOG_LEVEL or INFO)
        log_dir: Directory for log files
        enable_console: Enable console output
        enable_file: Enable file output with rotation
        enable_json: Enable JSON structured logs

    Returns:
        Configured logger instance
    """

    # Get log level from env or parameter
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Convert string to logging level
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Clear existing handlers
    logger.handlers = []

    # Create log directory if it doesn't exist
    if enable_file or enable_json:
        os.makedirs(log_dir, exist_ok=True)

    # 1. Console Handler (human-readable)
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(SimpleFormatter())
        logger.addHandler(console_handler)

    # 2. File Handler with rotation (human-readable)
    if enable_file:
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, "m4markets_agent.log"),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(SimpleFormatter())
        logger.addHandler(file_handler)

    # 3. JSON Handler for structured logging (daily rotation)
    if enable_json:
        json_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "m4markets_agent_structured.json"),
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days of logs
            encoding='utf-8'
        )
        json_handler.setLevel(numeric_level)
        json_handler.setFormatter(StructuredFormatter())
        logger.addHandler(json_handler)

    # 4. Error-only Handler
    error_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "errors.log") if (enable_file or enable_json) else "/dev/null",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(SimpleFormatter())
    logger.addHandler(error_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    logger.info(f"Logger '{name}' initialized at level {log_level}")

    return logger


def get_logger(name="m4markets-agent"):
    """
    Get or create a logger instance

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # Setup if not already configured
    if not logger.handlers:
        return setup_logger(name)

    return logger


# Convenience function for call-specific logging
def log_call_event(logger, level, message, call_id=None, lead_phone=None, **kwargs):
    """
    Log a call-related event with structured data

    Args:
        logger: Logger instance
        level: Log level (INFO, WARNING, ERROR, etc.)
        message: Log message
        call_id: Optional call ID
        lead_phone: Optional lead phone number
        **kwargs: Additional custom fields
    """
    extra = {}
    if call_id:
        extra["call_id"] = call_id
    if lead_phone:
        extra["lead_phone"] = lead_phone

    # Add any additional kwargs
    extra.update(kwargs)

    # Log with extra fields
    logger.log(getattr(logging, level.upper()), message, extra=extra)


# Example usage functions
def log_call_started(logger, call_id, lead_phone):
    """Log when a call starts"""
    log_call_event(
        logger, "INFO",
        f"Call started with {lead_phone}",
        call_id=call_id,
        lead_phone=lead_phone
    )


def log_call_ended(logger, call_id, lead_phone, duration, outcome):
    """Log when a call ends"""
    log_call_event(
        logger, "INFO",
        f"Call ended: {outcome}",
        call_id=call_id,
        lead_phone=lead_phone,
        duration=duration,
        outcome=outcome
    )


def log_error_with_context(logger, error, call_id=None, **context):
    """Log an error with full context"""
    log_call_event(
        logger, "ERROR",
        f"Error occurred: {str(error)}",
        call_id=call_id,
        error_type=type(error).__name__,
        **context
    )
