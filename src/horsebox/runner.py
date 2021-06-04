import bjoern
import pathlib
from minicli import cli, run
from rutter.urlmap import URLMap
from horsebox.project import make_project


@cli
def http(configfile: pathlib.Path):

    project = make_project(configfile)
    project.logger.info(
         f'Horsebox is boostrapping your project: {project.name}')

    with project.environment():
        root = URLMap()
        for name, app in project.apps.items():
            root[name] = app

        project.scan()

        try:
            if not project.server.socket:
                project.logger.info(
                    "Server started on "
                    f"http://{project.server.host}:{project.server.port}")
                bjoern.run(
                    root, project.server.host,
                    int(project.server.port), reuse_port=True)
            else:
                project.logger.info(
                    f"Server started on socket {project.server.socket}.")
                bjoern.run(root, project.server.socket)
        except KeyboardInterrupt:
            pass
        finally:
            #tasker.stop()
            pass


def serve():
    run()
