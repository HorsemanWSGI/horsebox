import os
import re
import colorlog
import contextlib
import logging
import importscan
from functools import reduce
from types import ModuleType
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
    mw = reduce(lambda x, y: y(x), reversed(middlewares), canonic)
    mw.__wrapped__ = canonic
    return mw


IGNORED_MODULES = [
    re.compile("tests$").search,
    re.compile("testing$").search
]


def modules_loader(*modules: ModuleType):
    for module in modules:
        importscan.scan(module, ignore=IGNORED_MODULES)
