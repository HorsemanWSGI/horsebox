import pathlib
import minicli
import gc
import logging
from loguru import logger
from typing import Any, TypeVar, Mapping
from hyperpyyaml import load_hyperpyyaml
from horsebox.types import Project
from horsebox.project import DefaultProject


LOGGING_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}


class InterceptHandler(logging.Handler):

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth, exception=record.exc_info).log(
                level, record.getMessage())


def get_project(config: Mapping[Any, Any]) -> Project:
    """Create a project from a config mapping.
    """
    factory: TypeVar[Project] = config.get('project', DefaultProject)
    if not issubclass(factory, Project):
        raise TypeError(
            'A Project factory needs a `horsebox.types.Project` subclass.')

    project: Project = factory.from_config(config)
    return project


@minicli.cli
def check(configfile: pathlib.Path):
    with configfile.open('r') as f:
        config: dict = load_hyperpyyaml(f)

    factory: TypeVar[Project] = config.get('project', DefaultProject)
    factory.check_config(config)


@minicli.cli
@minicli.cli('loglevel', choices=list(LOGGING_LEVELS.keys()))
def run(configfile: pathlib.Path, loglevel: str = 'info'):

    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=LOGGING_LEVELS[loglevel]
    )

    with configfile.open('r') as f:
        config: dict = load_hyperpyyaml(f)

    # We create a Project object to oversee the running.
    project: Project = get_project(config)

    # Cleaning up the unused bits of conf.
    del config
    gc.collect()

    logger.info('Horsebox is starting...')
    try:
        project.start()
    except KeyboardInterrupt:
        logger.info('Horsebox is shutting down...')
    finally:
        project.stop()
    logger.info('Horsebox stopped. Goodbye.')


def main():
    minicli.run()
