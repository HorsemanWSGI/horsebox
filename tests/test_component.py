import pytest
from horsebox.parsing import parse_component


class Factory:
    pass


class FactoryWithArgs:

    def __init__(self, name, url='http://example.com'):
        self.name = name
        self.url = url


def function():
    return 'yeah'


def function_with_args(name, age=18):
    if age > 18:
        return f'{name} is an adult.'
    return f'{name} is a child.'


class TestComponent:

    def test_factory_or_component(self):
        with pytest.raises(RuntimeError) as exc:
            parse_component({
                'factory': Factory,
                'component': function
            })
        assert str(exc.value) == (
            "A component definition needs either a 'factory' "
            "or a 'component' key : at least one and not both"
        )

    def test_factory(self):
        component = parse_component({
            'factory': Factory
        })
        assert isinstance(component, Factory)

        component = parse_component({
            'factory': FactoryWithArgs,
            'config': {
                'name': 'MacBeth'
            }
        })
        assert isinstance(component, FactoryWithArgs)
        assert component.name == 'MacBeth'
        assert component.url == 'http://example.com'

        component = parse_component({
            'factory': FactoryWithArgs,
            'config': {
                'url': 'http://google.fr',
                'name': 'MacBeth'
            }
        })
        assert isinstance(component, FactoryWithArgs)
        assert component.name == 'MacBeth'
        assert component.url == 'http://google.fr'

    def test_factory_missing_args(self):
        with pytest.raises(TypeError) as exc:
            parse_component({
                'factory': FactoryWithArgs,
            })
        assert str(exc.value) == (
            "__init__() missing 1 required positional argument: 'name'")

    def test_factory_too_many_args(self):
        with pytest.raises(TypeError) as exc:
            parse_component({
                'factory': Factory,
                'config': {
                    "foo": "bar"
                }
            })
        assert str(exc.value) == (
            "got an unexpected keyword argument 'foo'")

    def test_component(self):
        import functools

        component = parse_component({
            'component': function
        })
        assert component is function

        component = parse_component({
            'component': function_with_args,
            'config': {
                'name': 'MacBeth'
            }
        })
        assert isinstance(component, functools.partial)
        assert component.func is function_with_args
        assert component.args == ('MacBeth',)
        assert component.keywords == {}

    def test_component_too_many_args(self):
        with pytest.raises(TypeError) as exc:
            parse_component({
                'component': function,
                'config': {
                    'name': 'MacBeth'
                }
            })
        assert str(exc.value) == (
            "got an unexpected keyword argument 'name'")

        with pytest.raises(TypeError) as exc:
            parse_component({
                'component': function_with_args,
                'config': {
                    'name': 'MacBeth',
                    'thanedom': ['Glamis', 'Cawdor']
                }
            })
        assert str(exc.value) == (
            "got an unexpected keyword argument 'thanedom'")
