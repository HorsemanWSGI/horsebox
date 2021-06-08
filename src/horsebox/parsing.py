from omegaconf.listconfig import ListConfig
from omegaconf.dictconfig import DictConfig
from functools import reduce, partial
from typing import Union, Iterable, Optional
from types import ModuleType
from horsebox.types import WSGICallable, WSGIServer, WSGIMiddleware


def apply_middlewares(
        app: WSGICallable,
        middlewares: Iterable[WSGIMiddleware]) -> WSGICallable:
    return reduce(lambda x, y: y(x), reversed(middlewares), app)


def iter_components(components: DictConfig):
    for name, definition in components.items():
        factory = definition.get('factory')
        component = definition.get('component')
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

        if (middlewares := definition.get('middlewares')) is not None:
            if not isinstance(middlewares, (ListConfig, list)):
                raise TypeError(
                    "Middlewares can only be defined as a "
                    "list of callables. See the 'component' statement."
                )
            component = apply_middlewares(component, middlewares)

        yield name, component


def iter_modules(conf: Optional[Union[ListConfig, DictConfig]]):
    if conf is not None:
        if isinstance(conf, (ListConfig, list)):
            modules = conf
        elif isinstance(conf, (DictConfig, dict)):
            modules = conf.values()
        else:
            raise TypeError(
                "Modules can only be defined as a list of a dict "
                "with the module as key and a description as a value."
            )
        seen = set()
        for module in modules:
            if not isinstance(module, ModuleType):
                raise TypeError(
                    "Modules can only reference ModuleType elements. "
                    f"Got {type(module)} instead."
                )
            if module not in seen:
                yield module
                seen.add(module)


def prepare_server(server: DictConfig) -> WSGIServer:
    if server is None:
        return None
    factory = server.factory
    if factory is None:
        raise RuntimeError('Missing factory for server')
    return partial(factory, **server.config)
