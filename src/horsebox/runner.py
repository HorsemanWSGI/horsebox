import pathlib
import minicli
import gc
from typing import TypeVar
from hyperpyyaml import load_hyperpyyaml
from horsebox.types import Project
from horsebox.project import DefaultProject


@minicli.cli
def check(configfile: pathlib.Path):
    with configfile.open('r') as f:
        config: dict = load_hyperpyyaml(f)

    factory: TypeVar[Project] = config.get('project', DefaultProject)
    factory.check_config(config)


@minicli.cli
def run(configfile: pathlib.Path):

    with configfile.open('r') as f:
        config: dict = load_hyperpyyaml(f)

    factory: TypeVar[Project] = config.get('project', DefaultProject)
    if not issubclass(factory, Project):
        raise TypeError(
            'A Project factory needs a `horsebox.tyes.Project` subclass.')

    project: Project = factory.from_config(config)

    # Cleaning up the unused bits of conf.
    del config
    gc.collect()

    project.logger.info('Horsebox is starting...')
    try:
        project.start()
    except KeyboardInterrupt:
        project.logger.info('Horsebox is shutting down...')
    finally:
        project.stop()
    project.logger.info('Horsebox stopped. Goodbye.')


def main():
    minicli.run()
