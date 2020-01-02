import warnings
from typing import Callable, Optional


class Deprecated:
    def __init__(self, fn: Callable, message: Optional[str] = None):

        if message is None:
            message = f"{fn.__name__()} is deprecated. See documentation for "\
                "suggested alternative"

        self.message = message
        self.fn = fn

    def __call__(self, *args, **kwargs):
        warnings.warn(self.message, DeprecationWarning)
        return self.fn(*args, **kwargs)


def deprecated(message: Optional[str] = None):
    def _deprecated(fn: Callable):
        return Deprecated(fn, message)
    return _deprecated
