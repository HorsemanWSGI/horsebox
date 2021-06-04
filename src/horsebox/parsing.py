from omegaconf import OmegaConf
from functools import reduce, partial


def apply_middlewares(app, *middlewares):
    wrapped = reduce(lambda x, y: y(x), reversed(middlewares), app)
    wrapped.__wrapped__ = app
    return wrapped


def iter_components(config: OmegaConf):
    for name, metadata in config.items():
        factory = metadata.factory
        if factory is None:
            raise RuntimeError(
                f'Missing factory for component {name!r}')
        if metadata.config:
            yield name, factory(**metadata.config)
        else:
            yield name, factory()


def iter_apps(config: OmegaConf):
    for name, metadata in config.items():
        factory = metadata.factory
        if factory is None:
            raise RuntimeError(
                f'Missing factory for component {name!r}')

        if metadata.config:
            app = factory(**metadata.config)
        else:
            app = factory()
        if metadata.middlewares:
            app = apply_middlewares(app, *metadata.middlewares)

        yield name, app, metadata.modules


def prepare_server(config: OmegaConf):
    factory = config.factory
    if factory is None:
        raise RuntimeError('Missing factory for server')
    return partial(factory, **config.config)
