import os
import colorlog
import contextlib
import logging
from functools import reduce
from typing import Iterable, Callable, Any


@contextlib.contextmanager
def environment(environ: dict):
    """Temporarily set the process environment variables.
    """
    old_environ = dict(os.environ)
    os.environ.update(dict(environ))
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


def make_logger(name, level=logging.DEBUG) -> logging.Logger:
    logger = colorlog.getLogger(name)
    logger.setLevel(level)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(red)s%(levelname)-8s%(reset)s '
        '%(yellow)s[%(name)s]%(reset)s %(green)s%(message)s'))
    logger.addHandler(handler)
    return logger


def apply_middlewares(canonic: Any, middlewares: Iterable[Callable]):
    return reduce(lambda x, y: y(x), reversed(middlewares), canonic)
