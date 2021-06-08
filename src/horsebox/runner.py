import pathlib
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
         f'Horsebox is boostrapping {project.name!r}')
    try:
        project.start()
    except KeyboardInterrupt:
         project.logger.info(f'{project.name!r} shutting down.')
    finally:
        project.stop()
        project.logger.info("Goodbye.")


def serve():
    run()
