import re
import importscan
import logging
import pathlib
import hyperpyyaml
from types import ModuleType
from typing import Any, NamedTuple, Optional, Mapping, List, Callable
from dataclasses import dataclass, field
from horsebox.utils import environment, make_logger



Runner = Worker = Callable[[Any], Any]
scan_ignore_modules = [
    re.compile('tests$').search,
    re.compile('testing$').search
]


class Configuration(NamedTuple):
    name: str
    components: Mapping[str, Any]
    environ: Mapping[str, str]
    modules: List[ModuleType]
    workers: Mapping[str, Worker]
    runners: Mapping[str, Runner]

    @classmethod
    def from_yaml(cls, configfile: pathlib.Path):
        with configfile.open("r") as f:
            config: dict = hyperpyyaml.load_hyperpyyaml(f)
        return cls(
            name=config.get('name', 'Unnamed project'),
            components=config.get('components', {}),
            environ=config.get('environ', {}),
            modules=config.get('modules', []),
            runners=config.get('runners', {}),
            workers=config.get('workers', {})
        )

    def __add__(self, config: 'Configuration'):
        return self.__class__(
            name=config.name,  # override
            components={**self.components, **config.components},
            environ={**self.environ, **config.environ},
            modules=self.modules + config.modules,
            runners={**self.runners, **config.runners},
            workers={**self.workers, **config.workers}
        )


@dataclass
class Project:
    logger: logging.Logger
    config: Configuration
    workers: List[Worker] = field(default_factory=list)

    @classmethod
    def from_configs(cls, *configs: Configuration):
        if len(configs) == 1:
            config = configs[0]
        else:
            config = sum(configs)
        logger = make_logger(config.name)
        return cls(config=config, logger=logger)

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
