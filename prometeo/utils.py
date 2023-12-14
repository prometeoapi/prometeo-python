import asyncio
import functools


def adapt_async_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return func(*args, **kwargs)
            else:
                return loop.run_until_complete(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)

    return wrapper
