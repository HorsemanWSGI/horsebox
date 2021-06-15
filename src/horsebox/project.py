import re
import importscan
from typing import Any, Optional, Dict, List
from logging import Logger
from types import ModuleType
from horsebox.types import Runner, Worker, Project
from horsebox.utils import environment
from typeguard import typechecked
from horsebox.utils import make_logger


IGNORED_MODULES = [
    re.compile("tests$").search,
    re.compile("testing$").search
]


class DefaultProject(Project):

    __slots__ = ("logger", "runner", "modules", "workers", "environ")

    @typechecked
    def __init__(self,
                 name: str,
                 runner: Optional[Runner],
                 environ: Dict[str, str],
                 modules: List[ModuleType],
                 workers: Dict[str, Worker]):
        self.name = name
        self.runner = runner
        self.environ = environ
        self.modules = modules
        self.workers = workers
        self.logger: Logger = make_logger(name)

    @classmethod
    def check_config(cls, config: Dict[str, Any]):
        try:
            cls.from_config(config)
        except TypeError:
            raise
        else:
            print("Configuration is OK.")

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls(
            name=config.get('name', 'Unnamed project'),
            runner=config.get('runner'),
            environ=config.get('eviron', {}),
            modules=config.get('modules', []),
            workers=config.get('workers', {}),
        )

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
                self.logger.info("Starting service.")
                self.runner()
        else:
            if self.modules:
                self.scan()
            self.logger.info("Starting service.")
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
