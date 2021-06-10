import pathlib
import minicli
from hyperpyyaml import load_hyperpyyaml
from logging import Logger
from horsebox.project import Configuration, Project
from horsebox.utils import make_logger


@minicli.cli
def run(runner: str, configfile: pathlib.Path, no_worker: bool = False):

    with configfile.open('r') as f:
        config: dict = load_hyperpyyaml(f)

    logger: Logger = make_logger(config.get('name', 'Unnamed project'))
    project: Project = Project(logger=logger, config=Configuration(
        environ=config.get('environ', {}),
        modules=config.get('modules', []),
        workers=config.get('workers', {}),
        runners=config.get('runners', {})
    ))

    project.logger.info('Horsebox is starting...')
    try:
        project.start(runner, no_worker)
    except KeyboardInterrupt:
        project.logger.info('Horsebox is shutting down...')
    finally:
        project.stop()
    project.logger.info('Horsebox stopped. Goodbye.')


def main():
    minicli.run()
