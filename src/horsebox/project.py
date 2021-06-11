import re
import importscan
from typing import Optional
from logging import Logger
from horsebox.types import Runner, Workers, Modules, Environ
from horsebox.utils import environment
from typeguard import typechecked
from horsebox.utils import make_logger


IGNORED_MODULES = [
    re.compile('tests$').search,
    re.compile('testing$').search
]


class Project:

    __slots__ = ('logger', 'runner', 'modules', 'workers', 'environ')

    @typechecked
    def __init__(self,
                 name: str,
                 runner: Optional[Runner],
                 environ: Environ,
                 modules: Modules,
                 workers: Workers):
        self.logger: Logger = make_logger(name)
        self.runner = runner
        self.environ = environ
        self.modules = modules
        self.workers = workers

    def scan(self, ignore=IGNORED_MODULES):
        for module in self.modules:
            self.logger.info(f"... scanning module {module.__name__!r}")
            importscan.scan(module, ignore=ignore)

    def start(self):
        if self.workers:
            for name, worker in self.workers.items():
                self.logger.info(f"... worker {name!r} starts")
                worker.start()

        if self.environ:
            self.logger.info("... setting up environment")
            with environment(self.environ):
                if self.modules:
                    self.scan()
                self.logger.info(f"Starting service.")
                self.runner()
        else:
            if self.modules:
                self.scan()
            self.logger.info(f"Starting service.")
            self.runner()

    def stop(self):
        if self.workers:
            self.logger.info("... Shutting down workers")
            for name, worker in self.workers.items():
                if worker.is_alive():
                    worker.join(1)
                    self.logger.info(f"Worker {name!r} stopped.")
                else:
                    self.logger.info(
                        f"Worker {name!r} was already stopped.")
