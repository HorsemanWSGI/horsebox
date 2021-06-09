from omegaconf.listconfig import ListConfig
from omegaconf.dictconfig import DictConfig
from functools import reduce, partial
from inspect import signature
from typing import Union, Iterable, Optional, Callable, Any
from types import ModuleType


def apply_middlewares(canonic: Any, middlewares: Iterable[Callable]):
    return reduce(lambda x, y: y(x), reversed(middlewares), canonic)


def parse_component(definition: Union[DictConfig, dict]):
    factory = definition.get('factory')
    component = definition.get('component')
    if not (factory is not None) ^ (component is not None):
        raise RuntimeError(
            "A component definition needs either a 'factory' "
            "or a 'component' key : at least one and not both"
        )

    config = definition.get('config')
    if config is None:
        if factory is not None:
            component = factory()
    else:
        if factory is not None:
            sig = signature(factory)
            bound = sig.bind(**config)
            component = factory(*bound.args, **bound.kwargs)
        else:
            sig = signature(component)
            bound = sig.bind(**config)
            component = partial(component, *bound.args, **bound.kwargs)

    if (middlewares := definition.get('middlewares')) is not None:
        if not isinstance(middlewares, (ListConfig, list)):
            raise TypeError(
                "Middlewares can only be defined as a "
                "list of callables. See the 'component' statement."
            )
        component = apply_middlewares(component, middlewares)
    return component


def iter_components(components: DictConfig):
    for name, definition in components.items():
        yield name, parse_component(definition)


def iter_modules(conf: Union[ListConfig, DictConfig]):
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
