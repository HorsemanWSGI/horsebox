import colorlog
import contextlib
import importscan
import logging
import os
import pathlib
from rutter.urlmap import URLMap
from omegaconf import OmegaConf
from typing import NamedTuple, Callable, Optional
from zope.dottedname import resolve
from horsebox.parsing import iter_apps, iter_components, prepare_server


class Project(NamedTuple):
    name: str
    apps: dict
    components: dict
    environ: dict
    modules: list
    logger: logging.Logger
    server: Optional[Callable]

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
            self.logger.info(f"... scanning module {module.__name__}")
            importscan.scan(module)

    def run(self):
        with self.environment():
            root = URLMap()
            for name, app in self.apps.items():
                root[name] = app
            self.scan()
            self.logger.info(f"{self.name} server starts.")
            self.server(root)


def make_logger(name, level=logging.DEBUG) -> logging.Logger:
    logger = colorlog.getLogger(name)
    logger.setLevel(level)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(red)s%(levelname)-8s%(reset)s '
        '%(yellow)s[%(name)s]%(reset)s %(green)s%(message)s'))
    logger.addHandler(handler)
    return logger


def make_project(configfile, override: OmegaConf = None):

    components = {}
    apps = {}
    modules = []

    OmegaConf.register_resolver(
        "path", pathlib.Path)
    OmegaConf.register_resolver(
        "class", resolve.resolve)
    OmegaConf.register_resolver(
        "component", lambda name: components[name])

    config = OmegaConf.load(configfile)
    if override is not None:
        config = OmegaConf.merge(config, override)

    if not OmegaConf.is_missing(config, "components"):
        components.update(iter_components(config.components))

    if not OmegaConf.is_missing(config, "apps"):
        for name, app, dependencies in iter_apps(config.apps):
            apps[name] = app
            if dependencies is not None:
                modules.extend(dependencies)

    if not OmegaConf.is_missing(config, "server"):
        server = prepare_server(config.server)
    else:
        server = None

    name = config.name or 'Unnamed project'
    return Project(
        name=name,
        components=components,
        apps=apps,
        environ=config.environ,
        modules=modules,
        logger=make_logger(name),
        server=server
    )
