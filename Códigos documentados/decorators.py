import time
import logging

from functools import wraps
from utils.logger import LOGGER_NAME


# Creates the Logger (to record program events)
logger = logging.getLogger(LOGGER_NAME)


def log_time(func):
    # Creates a decorator (records informations for a function)
    @wraps(func)

    # Calculates code execution time
    def wrapper_decorator(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        # Formats the message to be shown
        # (which informs the execution time of a function)
        logger.info(f"{func.__name__!r} was executed in "
                    f"{run_time:.6f} seconds")

        return value

    return wrapper_decorator
