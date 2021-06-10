import pathlib
import minicli
from hyperpyyaml import load_hyperpyyaml
from logging import Logger
from horsebox.project import Configuration, Project
from horsebox.utils import make_logger


@minicli.cli
def run(*configfiles: pathlib.Path,
        runner: str = 'main',
        no_worker: bool=False):

    config = None
    for configfile in reversed(configfiles):
        with configfile.open("r") as f:
            #if config is not None:
            #    config: dict = load_hyperpyyaml(f, overrides=config)
            #else:
                config: dict = load_hyperpyyaml(f)

    config: Configuration = Configuration(
        environ=config.get('environ', {}),
        modules=config.get('modules', []),
        workers=config.get('workers', {}),
        runners=config.get('runners', {})
    )

    logger: Logger = make_logger(config.get('name', 'Unnamed project'))
    project: Project = Project(config=config, logger=logger)

    project.logger.info(
        f'Horsebox is boostrapping {project.config.name!r}')
    try:
        project.start(runner, no_worker)
    except KeyboardInterrupt:
        project.logger.info(f'{project.config.name!r} shutting down.')
    finally:
        project.stop()
    project.logger.info('Horsebox stopped.')


def main():
    minicli.run()
