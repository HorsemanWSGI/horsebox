import colorlog
import contextlib
import importscan
import logging
import os
import pathlib
from omegaconf import OmegaConf
from typing import NamedTuple
from zope.dottedname import resolve
from horsebox.parsing import iter_apps, iter_components


class Project(NamedTuple):
    name: str
    apps: dict
    components: dict
    environ: dict
    server: dict
    modules: list
    logger: logging.Logger

    @contextlib.contextmanager
    def environment(self):
        """Temporarily set the process environment variables.
        """
        self.logger.info(f"Setting up environment for project {self.name}")
        old_environ = dict(os.environ)
        os.environ.update(dict(self.environ))
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(old_environ)

    def scan(self):
        for module in self.modules:
            self.logger.info(f"Scanning module {module.__name__}")
            importscan.scan(module)


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
        "component", lambda namme: components[name])

    config = OmegaConf.load(configfile)
    if override is not None:
        config = OmegaConf.merge(config, override)

    components.update(dict(iter_components(config)))
    for name, app, modules in iter_apps(config):
        apps[name] = app
        if modules:
            modules.extend(modules)

    name = config.name or 'Unnamed project'
    return Project(
        name=name,
        components=components,
        apps=apps,
        environ=config.environ,
        server=config.server,
        modules=modules,
        logger=make_logger(name)
    )
