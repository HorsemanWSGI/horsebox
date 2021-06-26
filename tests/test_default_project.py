import pytest
from horsebox.project import DefaultProject


class TestDefaultProject:

    def test_instanciation(self):
        with pytest.raises(TypeError) as exc:
            DefaultProject()
        assert str(exc.value) == "missing a required argument: 'name'"

        with pytest.raises(TypeError) as exc:
            DefaultProject('My project')
        assert str(exc.value) == "missing a required argument: 'environ'"

        with pytest.raises(TypeError) as exc:
            DefaultProject('My project', environ={})
        assert str(exc.value) == "missing a required argument: 'loaders'"

        with pytest.raises(TypeError) as exc:
            DefaultProject('My project', environ={}, loaders=[], modules=[])
        assert str(exc.value) == "missing a required argument: 'workers'"

        project = DefaultProject(
            'My project',
            environ={},
            loaders=[],
            workers={}
        )
        assert project.name == 'My project'

    def test_type_checking(self):
        with pytest.raises(TypeError) as exc:
            DefaultProject(
                'My project',
                environ=[],
                loaders=[],
                workers={}
            )
        assert str(exc.value) == (
            'type of argument "environ" must be a dict; got list instead')

        with pytest.raises(TypeError) as exc:
            DefaultProject(
                'My project',
                environ={},
                loaders=[],
                workers=[]
            )
        assert str(exc.value) == (
            'type of argument "workers" must be a dict; got list instead')

        with pytest.raises(TypeError) as exc:
            DefaultProject(
                'My project',
                environ={},
                loaders=[],
                workers={'test': object}
            )
        assert str(exc.value) == (
            '''type of argument "workers"['test'] must be one of '''
            '''(Process, Thread); got object instead''')

    def test_type_environ(self):
        with pytest.raises(TypeError) as exc:
            DefaultProject(
                'My project',
                environ={'test': 1},
                loaders=[],
                workers={}
            )
        assert str(exc.value) == (
            '''type of argument "environ"['test'] must be str; '''
            '''got int instead''')

        with pytest.raises(TypeError) as exc:
            DefaultProject(
                'My project',
                environ={1: 'test'},
                loaders=[],
                workers={}
            )
        assert str(exc.value) == (
            '''type of keys of argument "environ" must be str; '''
            '''got int instead'''
        )
