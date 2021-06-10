import importscan
import logging
import pathlib
import hyperpyyaml
from types import ModuleType
from typing import Any, NamedTuple, Optional, Mapping, List, Callable
from horsebox.utils import environment, make_logger


Runner = Worker = Callable[[Any], Any]


class Configuration(NamedTuple):
    name: str
    components: Mapping[str, Any]
    environ: Mapping[str, str]
    modules: List[ModuleType]
    workers: Mapping[str, Worker]
    runner: Optional[Runner] = None

    @classmethod
    def from_yaml(cls, configfile: pathlib.Path):
        with configfile.open("r") as f:
            config: dict = hyperpyyaml.load_hyperpyyaml(f)
        if 'components' not in config:
            config['components'] = {}
        if 'name' not in config:
            config['name'] = 'Unnamed project'
        return cls(
            name=config.get('name', 'Unnamed project'),
            components=config.get('components', {}),
            environ=config.get('environ', {}),
            modules=config.get('modules', []),
            workers=config.get('workers', {}),
            runner=config.get('runner')
        )

    def __add__(self, config: 'Configuration'):
        return self.__class__(
            name=config.name,  # override
            runner=config.runner,  # override
            components={**self.components, **config.components},
            environ={**self.environ, **config.environ},
            modules=self.modules + config.modules,
            workers={**self.workers, **config.workers},
        )


class Project(NamedTuple):
    logger: logging.Logger
    config: Configuration

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
            importscan.scan(module)

    def _run(self):
        self.scan()
        for name, worker in self.config.workers.items():
            self.logger.info(f"... worker {name!r} starts")
            worker.start()
        self.logger.info(f"{self.config.name!r} runner starts.")
        self.config.runner()

    def start(self):
        if self.config.environ:
            self.logger.info("... setting up environment")
            with environment(self.config.environ):
                self._run()
        else:
            self._run()

    def stop(self):
        for name, worker in self.config.workers.items():
            self.logger.info(f"... worker {name!r} stops")
            worker.stop()
