import colorlog
import contextlib
import importscan
import logging
import os
import pathlib
from omegaconf import OmegaConf
from typing import Any, NamedTuple, Mapping, List, Callable
from zope.dottedname import resolve
from types import ModuleType
from horsebox.parsing import iter_components, iter_modules, parse_component


Runner = Worker = Callable[[], None]


class Project(NamedTuple):
    name: str
    runner: Runner
    components: Mapping[str, Any]
    environ: Mapping[str, str]
    modules: List[ModuleType]
    workers: Mapping[str, Worker]
    logger: logging.Logger

    @contextlib.contextmanager
    def environment(self):
        """Temporarily set the process environment variables.
        """
        self.logger.info("... setting up environment")
        old_environ = dict(os.environ)
        os.environ.update(dict(self.environ))
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(old_environ)

    def scan(self):
        for module in self.modules:
            self.logger.info(f"... scanning module {module.__name__!r}")
            importscan.scan(module)

    def _run(self):
        self.scan()
        if self.workers:
            for name, worker in self.workers.items():
                self.logger.info(f"... worker {name!r} starts")
                worker.start()
        self.logger.info(f"{self.name!r} runner starts.")
        self.runner()

    def start(self):
        if self.environment:
            with self.environment():
                self._run()
        else:
            self._run()

    def stop(self):
        if self.workers:
            for name, worker in self.workers.items():
                self.logger.info(f"... worker {name!r} stops")
                worker.stop()


def make_logger(name, level=logging.DEBUG) -> logging.Logger:
    logger = colorlog.getLogger(name)
    logger.setLevel(level)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(red)s%(levelname)-8s%(reset)s '
        '%(yellow)s[%(name)s]%(reset)s %(green)s%(message)s'))
    logger.addHandler(handler)
    return logger


def make_project(configfiles: List[pathlib.Path],
                 override: OmegaConf = None) -> Project:

    components: Mapping[str, Any] = {}

    OmegaConf.register_resolver("path", pathlib.Path)
    OmegaConf.register_resolver("dotted", resolve.resolve)
    OmegaConf.register_resolver("component", lambda name: components[name])

    config = None
    for configfile in configfiles:
        loaded = OmegaConf.load(configfile)
        if config is None:
            config = loaded
        else:
            config = OmegaConf.merge(config, loaded)

    if override is not None:
        config = OmegaConf.merge(config, override)

    if 'runner' not in config:
        # A runner is a mandatory callable that keeps the process alive.
        raise RuntimeError(
            "No declared runner: use 'horsebox.builtins.asyncio_loop' "
            "to run forever.")

    if 'components' in config:
        components.update(iter_components(config.components))

    runner: Runner = parse_component(config.runner)

    if 'workers' in config:
        workers: Mapping[str, Worker] = dict(
            iter_components(config.workers)
        )
    else:
        workers = None

    name = config.name or 'Unnamed project'
    return Project(
        name=name,
        components=components,
        environ=config.environ,
        workers=workers,
        modules=list(iter_modules(config.modules)),
        logger=make_logger(name),
        runner=runner
    )
