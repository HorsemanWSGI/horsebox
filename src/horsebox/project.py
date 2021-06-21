from typing import Any, Optional, Dict, List
from logging import Logger
from horsebox.types import Runner, Worker, Project, Loader
from horsebox.utils import environment
from typeguard import typechecked
from horsebox.utils import make_logger


class DefaultProject(Project):

    __slots__ = (
        "logger", "runner", "modules", "workers", "environ", "loaders")

    @typechecked
    def __init__(self,
                 name: str,
                 environ: Dict[str, str],
                 loaders: List[Loader],
                 workers: Dict[str, Worker],
                 logger: Optional[Logger] = None,
                 runner: Optional[Runner] = None):
        self.name = name
        self.runner = runner
        self.environ = environ
        self.loaders = loaders
        self.workers = workers
        if logger is None:
            logger: Logger = make_logger(name)
        self.logger = logger

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
            logger=config.get('logger'),
            environ=config.get('environ', {}),
            loaders=config.get('loaders', []),
            workers=config.get('workers', {}),
        )

    def load(self):
        for loader in self.loaders:
            loader()

    def start(self):
        if self.loaders:
            self.logger.info("... calling loaders")
            self.load()

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
            self.logger.info("Starting service.")
            self.runner()

    def stop(self):
        if self.workers:
            self.logger.info("... Shutting down workers")
            for name, worker in self.workers.items():
                if worker.is_alive():
                    worker.join()
                    self.logger.info(f"Worker {name!r} stopped.")
                else:
                    self.logger.info(
                        f"Worker {name!r} was already stopped.")
