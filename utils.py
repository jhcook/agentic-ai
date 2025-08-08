import logging
from functools import wraps

def log_to_file():
    '''Decorator to log function calls and exceptions to a file.

    This decorator logs the following information using the logger for the current module:
      - When the decorated function is called, including its arguments and keyword arguments.
      - The return value of the function after successful execution.
      - Any exceptions raised during the function execution, along with the full stack trace.

    Usage:
        @log_to_file()
        def my_function(...):
            ...

    Note:
        To ensure logs are written to a file, configure the logging system in your application,
        for example:
            import logging
            logging.basicConfig(filename='app.log', level=logging.DEBUG)
    '''
    logger = logging.getLogger(__name__)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator