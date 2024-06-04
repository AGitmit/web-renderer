import sys
import contextvars
import functools
import time
import asyncio

from loguru import logger
from web_renderer.config import config as conf

# Define a context variable for the log context
log_context = contextvars.ContextVar("context", default="No Context")


def init_logger(**context):
    "Set up a new logger"
    logger.remove()
    logger.add(
        sys.stdout,
        level=conf.log_level,
        enqueue=True,
        colorize=True,
        format="{time} | {level} | {extra} | {message}",
        backtrace=True,
        diagnose=True,
    )
    logger.configure(extra=context or {"source": "Internal"})
    return logger


logger = init_logger()


def log_execution_metrics(func):
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} took {execution_time:.4f} seconds to complete.")
        return result

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} took {execution_time:.4f} seconds to complete.")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
