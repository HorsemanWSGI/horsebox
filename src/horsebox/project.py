import colorlog
import contextlib
import importscan
import logging
import os
import pathlib
from rutter.urlmap import URLMap
from omegaconf import OmegaConf
from typing import Any, NamedTuple, Callable, Optional, Mapping, List
from zope.dottedname import resolve
from types import ModuleType
from horsebox.types import WSGICallable, WSGIServer, Worker
from horsebox.parsing import iter_components, iter_modules, prepare_server


class Project(NamedTuple):
    name: str
    apps: Mapping[str, WSGICallable]
    components: Mapping[str, Any]
    environ: Mapping[str, str]
    modules: List[ModuleType]
    workers: Mapping[str, Worker]
    logger: logging.Logger
    server: Optional[WSGIServer]

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

    def start(self):
        if self.server is None:
            raise NotImplementedError(
                f'No server defined for project {self.name!r}.')

        with self.environment():
            root = URLMap()
            for name, app in self.apps.items():
                root[name] = app
            self.scan()
            if self.workers:
                for name, worker in self.workers.items():
                    self.logger.info(f"... worker {name!r} starts")
                    worker.start()

            self.logger.info(f"{self.name!r} server starts.")
            self.server(root)

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

    if 'components' in config:
        components.update(iter_components(config.components))

    if 'apps' in config:
        apps: Mapping[str, WSGICallable] = dict(
            iter_components(config.apps)
        )
    else:
        apps = None

    if 'workers' in config:
        workers: Mapping[str, WSGICallable] = dict(
            iter_components(config.workers)
        )
    else:
        workers = None

    if 'server' in config:
        server: WSGIServer = prepare_server(config.server)
    else:
        server = None

    name = config.name or 'Unnamed project'
    return Project(
        name=name,
        components=components,
        apps=apps,
        environ=config.environ,
        workers=workers,
        modules=list(iter_modules(config.modules)),
        logger=make_logger(name),
        server=server
    )
