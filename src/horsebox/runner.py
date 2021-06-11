import pathlib
import minicli
import gc
from hyperpyyaml import load_hyperpyyaml
from logging import Logger
from horsebox.project import Project


@minicli.cli
def run(configfile: pathlib.Path, no_worker: bool = False):

    with configfile.open('r') as f:
        config: dict = load_hyperpyyaml(f)

    if no_worker:
        del config['workers']

    project: Project = Project(
        name=config.get('name', 'Unnamed project'),
        runner=config.get('runner'),
        workers=config.get('workers', {}),
        modules=config.get('modules', []),
        environ=config.get('environ', {}),
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
