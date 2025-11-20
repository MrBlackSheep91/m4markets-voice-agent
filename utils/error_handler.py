"""
Error Handling and Circuit Breaker Implementation for M4Markets Voice Agent
Provides robust error handling, retry logic, and circuit breaker patterns
"""

import asyncio
import functools
import time
from typing import Callable, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger("m4markets-agent.error_handler")


class CircuitBreakerState(Enum):
    """States for the circuit breaker"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation
    Prevents cascading failures by monitoring errors and opening the circuit
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""

        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")

        try:
            result = func(*args, **kwargs)

            # Success - reset if recovering
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED - service recovered")

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}: {str(e)}"
            )

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.error(
                    f"Circuit breaker OPEN after {self.failure_count} failures"
                )

            raise

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""

        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")

        try:
            result = await func(*args, **kwargs)

            # Success - reset if recovering
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED - service recovered")

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}: {str(e)}"
            )

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.error(
                    f"Circuit breaker OPEN after {self.failure_count} failures"
                )

            raise


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retry with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

            # Should never reach here, but just in case
            raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)

            # Should never reach here, but just in case
            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    log_error: bool = True,
    error_message: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Safely execute a function with error handling

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default_return: Value to return if function fails
        log_error: Whether to log errors
        error_message: Custom error message
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_return if it fails
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            msg = error_message or f"Error in {func.__name__}"
            logger.error(f"{msg}: {str(e)}", exc_info=True)
        return default_return


async def safe_execute_async(
    func: Callable,
    *args,
    default_return: Any = None,
    log_error: bool = True,
    error_message: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Safely execute an async function with error handling

    Args:
        func: Async function to execute
        *args: Positional arguments for the function
        default_return: Value to return if function fails
        log_error: Whether to log errors
        error_message: Custom error message
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_return if it fails
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        if log_error:
            msg = error_message or f"Error in {func.__name__}"
            logger.error(f"{msg}: {str(e)}", exc_info=True)
        return default_return


class ErrorRecovery:
    """Manages error recovery strategies"""

    @staticmethod
    async def reconnect_with_backoff(
        connect_func: Callable,
        max_attempts: int = 5,
        initial_delay: float = 2.0
    ) -> bool:
        """
        Attempt to reconnect to a service with exponential backoff

        Args:
            connect_func: Async function that establishes connection
            max_attempts: Maximum reconnection attempts
            initial_delay: Initial delay between attempts

        Returns:
            True if reconnection successful, False otherwise
        """
        delay = initial_delay

        for attempt in range(max_attempts):
            try:
                logger.info(f"Reconnection attempt {attempt + 1}/{max_attempts}")
                await connect_func()
                logger.info("Reconnection successful")
                return True

            except Exception as e:
                logger.warning(f"Reconnection attempt {attempt + 1} failed: {str(e)}")

                if attempt < max_attempts - 1:
                    logger.info(f"Waiting {delay:.1f}s before next attempt...")
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff

        logger.error(f"Failed to reconnect after {max_attempts} attempts")
        return False


# Global circuit breakers for different services
livekit_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60
)

database_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30
)

openai_circuit_breaker = CircuitBreaker(
    failure_threshold=10,
    recovery_timeout=120
)


# Decorator for protected LiveKit operations
def protected_livekit_call(func):
    """Decorator to protect LiveKit calls with circuit breaker"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await livekit_circuit_breaker.call_async(func, *args, **kwargs)
    return wrapper


# Decorator for protected database operations
def protected_db_call(func):
    """Decorator to protect database calls with circuit breaker"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await database_circuit_breaker.call_async(func, *args, **kwargs)
    return wrapper
