import asyncio
from typing import Mapping
from rutter.urlmap import URLMap


class HTTPRouter(URLMap):

    def __init__(self, applications: Mapping, **kwargs):
        super().__init__(**kwargs)
        for name, app in applications.items():
            self[name] = app


def asyncio_loop(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.close()
