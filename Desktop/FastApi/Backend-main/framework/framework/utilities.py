import functools
import asyncio
import threading


def run_once(func):
    '''
    This decorator wraps a function and makes sure it is executed only once for the lifetime of the process.
    Depending on whether the wrapped function is normal or async it wraps accordingly.
    It cache's the response returned by the original function and returns the cached response on subsequent calls.

    Usage:
    @run_once
    def foo():
        pass

    @run_once
    async def async_foo():
        pass
    
    '''
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with wrapper.lock:
                if (not wrapper.has_executed) or (not hasattr(wrapper, 'response')):
                    wrapper.has_executed = True # TODO: Should this be after the function execution, incase there is an exception!!!???
                    wrapper.response = await func(*args, **kwargs)
            return wrapper.response
        wrapper.lock = asyncio.Lock()
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with wrapper.lock:
                if not wrapper.has_executed:
                    wrapper.has_executed = True
                    wrapper.response = func(*args, **kwargs)
            return wrapper.response
                    
        wrapper.lock = threading.Lock()
    wrapper.has_executed = False
    return wrapper

