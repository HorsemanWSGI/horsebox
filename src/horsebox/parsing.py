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
        component = definition.component
        if not (factory is not None) ^ (component is not None):
            raise RuntimeError(
                "A component definition needs either a 'factory' "
                "or a 'component' key : at least one and not both"
            )

        if factory is not None:
            if definition.config:
                component = factory(**definition.config)
            else:
                component = factory()
        elif definition.config:
            # We have a 'component' declaration and some extra config.
            # It will be used as parameters for it
            component = partial(component, **definition.config)

        if definition.middlewares is not None:
            component = apply_middlewares(component, *definition.middlewares)

        yield name, component


def prepare_server(server: OmegaConf) -> WSGIServer:
    factory = server.factory
    if factory is None:
        raise RuntimeError('Missing factory for server')
    return partial(factory, **server.config)
