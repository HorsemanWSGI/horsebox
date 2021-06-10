import re
import importscan
import logging
import pathlib
from types import ModuleType
from typing import Any, NamedTuple, Mapping, Iterable, Callable, ClassVar
from dataclasses import dataclass, field
from horsebox.utils import environment, make_logger


Runner = Worker = Callable[[Any], Any]



class Configuration(NamedTuple):
    environ: Mapping[str, str]
    modules: Iterable[ModuleType]
    workers: Mapping[str, Worker]
    runners: Mapping[str, Runner]


class Project:
    logger: logging.Logger
    config: Configuration
    workers: Iterable[Worker] = field(default_factory=list)
    scan_ignore_modules: ClassVar[Iterable[Callable[[str], Any]]] = [
        re.compile('tests$').search,
        re.compile('testing$').search
    ]

    def scan(self):
        for module in self.config.modules:
            self.logger.info(f"... scanning module {module.__name__!r}")
            importscan.scan(module, ignore=scan_ignore_modules)

    def start(self, runner: str, no_worker: bool = False):
        if (service := self.config.runners.get(runner)) is None:
            raise NameError(f'Unknown runner {runner!r}.')

        if not no_worker:
            for name, worker in self.config.workers.items():
                self.logger.info(f"... worker {name!r} starts")
                worker.start()
                self.workers.append(worker)

        if self.config.environ:
            self.logger.info("... setting up environment")
            with environment(self.config.environ):
                self.scan()
                self.logger.info(f"Starting service {runner!r}.")
                service()
        else:
            self.scan()
            self.logger.info("Starting service {runner!r}.")
            service()

    def stop(self):
        if self.workers:
            self.logger.info(f"... Shutting down workers")
            for worker in self.workers:
                worker.stop()
