"""
Tool Call Tracking Decorator
Wraps tool functions to track usage and latency
"""

import time
import functools
import logging
from typing import Callable
from utils.cost_metrics import metrics_tracker

logger = logging.getLogger(__name__)


def track_tool_call(func: Callable) -> Callable:
    """
    Decorator to track tool call usage and latency

    Usage:
        @function_tool
        @track_tool_call
        async def my_tool(param: str) -> str:
            ...
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()

        logger.info(f"🔧 Tool STARTED: {tool_name}")
        logger.debug(f"   Args: {args[:2] if len(args) > 2 else args}")  # Limit arg logging

        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            logger.info(f"✅ Tool COMPLETED: {tool_name} ({duration:.2f}s)")

            # Note: call_id would need to be passed via context
            # For now, just log the tool call
            # In production, you'd use contextvars to get current call_id

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ Tool FAILED: {tool_name} ({duration:.2f}s) - {str(e)}")
            raise

    return wrapper


def log_tool_result(tool_name: str, result: any, max_length: int = 200):
    """Log tool result in a readable format"""

    if isinstance(result, str):
        preview = result[:max_length] + "..." if len(result) > max_length else result
        logger.debug(f"   Result preview: {preview}")
    elif isinstance(result, dict):
        logger.debug(f"   Result keys: {list(result.keys())}")
    else:
        logger.debug(f"   Result type: {type(result)}")
