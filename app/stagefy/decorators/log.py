from functools import wraps
from typing import Any, Callable, Type, TypeVar

from ..logging import logger

T = TypeVar('T')


def method_logger(function: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator responsible for logging method calls.

    Args:
        function (Callable[P, T]): Method to be decorated.

    Returns:
        Callable[P, T]: Decorated method.
    """

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        data: dict[str, Any] = {
            'module': function.__module__,
            'method': function.__qualname__,
            'args': args,
            'kwargs': kwargs,
        }
        log = ', '.join(f'{key}={value!r}' for key, value in data.items())

        logger.info(f'Running {function.__qualname__} method...')
        logger.debug(log)

        return function(*args, **kwargs)

    return wrapper


def set_class_logger(cls: Type[T]) -> Type[T]:
    """
    Class decorator responsible for decorating each class method with
    method_logger decorator.

    Args:
        cls (type[T]): Decorated class.

    Returns:
        type[T]: Decorated class.
    """

    for name, obj in vars(cls).items():
        if not name.endswith('_') and callable(obj):
            setattr(cls, name, method_logger(obj))

    return cls
