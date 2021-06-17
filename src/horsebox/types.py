from abc import ABC, abstractmethod, abstractclassmethod
from logging import Logger
from multiprocessing import Process
from threading import Thread
from typing import Any, Mapping, Callable, Union, NoReturn


class Project(ABC):
    """A generic project. The purpose of a Project is to take a
    configuration mapping and use it to start a collection of services,
    or processes in order to perform a task or setup an environment.
    Classical usage : HTTP server, AMQP workers, Async services...
    """

    logger: Logger

    @abstractmethod
    def start(self) -> NoReturn:
        """Start the project.
        This includes running everything before the main loop, if there's
        such a thing.
        """

    @abstractmethod
    def stop(self) -> NoReturn:
        """Stop the project.
        This stopping every running : processes, loops, queues
        and other services.
        """

    @abstractclassmethod
    def check_config(cls, config: Mapping[str, Any]) -> Any:
        """Check a configuration mapping.
        These checks are project-centric and depends on what your project
        actually needs to be started.
        """

    @abstractclassmethod
    def from_config(cls, config: Mapping[str, Any]) -> 'Project':
        """Instanciate the project from a configuration mapping.

        Note : the config is delete right after this method returns. Make
        sure that all the needed components from the conf are referenced.
        """


# A few basic useful types.
# -------------------------

Worker = Union[Process, Thread]  # non-block worker with a start/join API
# Can be created directly in the config
# example: !new:multiprocessing.Process
#   target: !name:print
#     - this is a worker


Runner = Callable[[], Any]  # A blocking worker that is start by a call
# Can be created directly in the config
# example: !name:horsebox.builtins.asyncio_loop
#   - !apply:asyncio.get_event_loop


Loader = Callable[[], Any]  # A loader prototype, to bootstrap registries
# Can be created directly in the config
# example: !name:my_project.my_registry.load
#   - !apply:pathlib.Path [/tmp/resources]
