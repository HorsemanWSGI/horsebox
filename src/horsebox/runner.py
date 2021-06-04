import pathlib
from minicli import cli, run
from horsebox.project import make_project


@cli
def http(configfile: pathlib.Path):

    project = make_project(configfile)
    project.logger.info(
         f'Horsebox is boostrapping your project: {project.name}')
    try:
        project.run()
    except KeyboardInterrupt:
         project.logger.info(f'{project.name} shutting down.')


def serve():
    run()
