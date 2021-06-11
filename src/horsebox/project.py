import re
import importscan
import logging
from types import ModuleType
from typing import Any, NamedTuple, Mapping, Iterable, Callable, ClassVar
from dataclasses import dataclass, field
from horsebox.utils import environment


Runner = Worker = Callable[[Any], Any]

scan_ignore_modules: Iterable[Callable[[str], Any]] = [
    re.compile('tests$').search,
    re.compile('testing$').search
]


class Project(NamedTuple):
    logger: logging.Logger
    runner: Runner
    environ: Mapping[str, str]
    modules: Iterable[ModuleType]
    workers: Mapping[str, Worker]

    def scan(self, ignore=scan_ignore_modules):
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
