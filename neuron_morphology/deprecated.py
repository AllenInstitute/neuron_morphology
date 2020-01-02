import warnings
from functools import partial
from typing import Callable, Optional


class Deprecated:
    def __init__(self, fn: Callable, message: Optional[str] = None):
        """ Wrapper for a deprecated function

        Parameters
        ----------
        fn : a function to be wrapped
        message : the warning message to be displayed when the wrapped function 
            is called. If not provided, a sensible default will be generated.
        
        Notes
        -----
        It would be good to unify this with allensdk.deprecated. However, we 
            have a use case that is not currently supported by allensdk: 
            deprecation of functions only when imported through certain modules

        """

        if message is None:
            message = f"{fn.__name__} is deprecated. See documentation for "\
                "suggested alternative"

        self.message = message
        self.fn = fn

    def __call__(self, *args, **kwargs):
        warnings.warn(self.message, DeprecationWarning)
        return self.fn(*args, **kwargs)


def deprecated(fn: Callable = None, message: Optional[str] = None):
    """ Decorate a function as deprecated. A warning will be emitted whenever 
    this function is called.

    Usage
    -----

    # generate a default warning message
    @deprecated
    def my_function():
        ...

    # use a custom warning message
    @deprecatd("my_message")
    def my_function():
        ...

    """

    if isinstance(fn, str) and message is None:
        # someone has invoked this decorator as deprecated("my message")
        message = fn
        fn = None

    if fn is not None:
        return Deprecated(fn, message)

    return partial(Deprecated, message=message)
