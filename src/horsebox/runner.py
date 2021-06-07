import pathlib
from typing import List
from minicli import cli, run
from omegaconf import OmegaConf
from horsebox.project import Project, make_project


@cli
def http(*configfiles: pathlib.Path):
    """HTTP Server runner
    """
    project: Project = make_project(
        configfiles, override=OmegaConf.from_cli())
    project.logger.info(
         f'Horsebox is boostrapping your project: {project.name}')
    try:
        project.run()
    except KeyboardInterrupt:
         project.logger.info(f'{project.name} shutting down.')


def serve():
    run()
