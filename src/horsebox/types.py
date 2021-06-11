from multiprocessing import Process
from threading import Thread
from types import ModuleType
from typing import Any, Mapping, Iterable, Callable, Union


Worker = Union[Process, Thread]
Runner = Callable[[], Any]
Workers = Mapping[str, Worker]
Modules = Iterable[ModuleType]
Environ = Mapping[str, str]
