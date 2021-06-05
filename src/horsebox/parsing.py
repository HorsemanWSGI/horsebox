from omegaconf import OmegaConf
from functools import reduce, partial
from horsebox.types import WSGICallable, WSGIServer


def apply_middlewares(app: WSGICallable, *middlewares) -> WSGICallable:
    wrapped = reduce(lambda x, y: y(x), reversed(middlewares), app)
    wrapped.__wrapped__ = app
    return wrapped


def iter_components(components: OmegaConf):
    for name, definition in components.items():
        factory = definition.factory
        if factory is None:
            raise RuntimeError(
                f'Missing factory for component {name!r}')
        if definition.config:
            yield name, factory(**definition.config)
        else:
            yield name, factory()


def iter_applications(applications: OmegaConf):
    for name, definition in applications.items():
        factory = definition.factory
        if factory is None:
            raise RuntimeError(
                f'Missing factory for component {name!r}')

        if definition.config is not None:
            app = factory(**definition.config)
        else:
            app = factory()
        if definition.middlewares is not None:
            app = apply_middlewares(app, *definition.middlewares)

        yield name, app, definition.modules


def prepare_server(server: OmegaConf) -> WSGIServer:
    factory = server.factory
    if factory is None:
        raise RuntimeError('Missing factory for server')
    return partial(factory, **server.config)
