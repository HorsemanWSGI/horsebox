import pathlib
import minicli
from horsebox.project import Configuration, Project


@minicli.cli
def run(*configfiles: pathlib.Path):
    """HTTP Server runner
    """
    configs = [Configuration.from_yaml(fpath) for fpath in configfiles]
    project: Project = Project.from_configs(*configs)

    project.logger.info(
        f'Horsebox is boostrapping {project.config.name!r}')
    try:
        project.start()
    except KeyboardInterrupt:
        project.logger.info(f'{project.config.name!r} shutting down.')
    finally:
        project.stop()
    project.logger.info('Horsebox stopped.')


def main():
    minicli.run()
