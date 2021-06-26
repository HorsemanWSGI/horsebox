from horsebox.types import Runner, Worker, Project, Loader
from horsebox.utils import environment
from loguru import logger
from typeguard import typechecked
from typing import Any, Optional, Dict, List


class DefaultProject(Project):

    __slots__ = ("environ", "loaders", "runner", "workers")

    @typechecked
    def __init__(self,
                 name: str,
                 environ: Dict[str, str],
                 loaders: List[Loader],
                 workers: Dict[str, Worker],
                 runner: Optional[Runner] = None):
        self.name = name
        self.runner = runner
        self.environ = environ
        self.loaders = loaders
        self.workers = workers

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
            environ=config.get('environ', {}),
            loaders=config.get('loaders', []),
            workers=config.get('workers', {}),
        )

    def start(self):

        @environment(self.environ)
        def project_runner():
            if self.loaders:
                logger.info("... calling loaders")
                for loader in self.loaders:
                    loader()

            if self.workers:
                for name, worker in self.workers.items():
                    logger.info(f"... worker {name!r} starts")
                    worker.start()

            logger.info("Starting service.")
            self.runner()

        return project_runner()

    def stop(self):
        if self.workers:
            logger.info("... Shutting down workers")
            for name, worker in self.workers.items():
                if worker.is_alive():
                    worker.join()
                    logger.info(f"Worker {name!r} stopped.")
                else:
                    logger.info(f"Worker {name!r} was already stopped.")
