import os
import re
import contextlib
import importscan
from loguru import logger
from functools import reduce
from types import ModuleType
from typing import Iterable, Callable, Any, Optional, Dict
from horsebox.types import OSEnviron


class environment(contextlib.ContextDecorator):
    """Temporarily set the process environment variables.
    """
    __slots__ = ('environ',)

    def __init__(self, environ: Optional[OSEnviron] = None):
        self.environ = environ

    def __enter__(self):
        if self.environ is not None:
            logger.info("... setting up environment")
            self.environ = dict(os.environ)
            os.environ.update(dict(self.environ))
        return self

    def __exit__(self, *exc):
        if self.environ is not None:
            logger.info("... restoring environment")
            os.environ.clear()
            os.environ.update(self.environ)
        return False


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
