import pathlib
import minicli
import gc
from hyperpyyaml import load_hyperpyyaml
from logging import Logger
from horsebox.project import Project
from horsebox.utils import make_logger


@minicli.cli
def run(service: str, configfile: pathlib.Path, no_worker: bool = False):

    with configfile.open('r') as f:
        config: dict = load_hyperpyyaml(f)

    logger: Logger = make_logger(config.get('name', 'Unnamed project'))

    if no_worker:
        del config['workers']

    runner = None
    if 'runners' in config:
        runner = config['runners'].get(service)

    if runner is None:
        raise LookupError(f'Runner {service!r} is not defined.')

    project: Project = Project(
        logger=logger,
        runner=runner,
        environ=config.get('environ', {}),
        modules=config.get('modules', []),
        workers=config.get('workers', {})
    )

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
