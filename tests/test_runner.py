import pytest
from horsebox.runner import get_project, main
from horsebox.types import Project
from horsebox.project import DefaultProject


class MyProject(Project):

    def __init__(self, name: str):
        self.name = name

    def start(self):
        pass

    def stop(self):
        pass

    @classmethod
    def check_config(cls, config):
        if name := config.get('name'):
            if isinstance(name, str):
                return True
        raise KeyError(
            "Expecting key `name` with a str type value.")

    @classmethod
    def from_config(cls, config):
        cls.check_config(config)
        return cls(config['name'])


@pytest.fixture(scope="session")
def config_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("conf").join("config.yaml")
    with fn.open('w+') as fd:
        fd.write(
            "runner: !name:print\n"
            "  - I am working"
        )
    return fn


class TestProjectExtraction:

    def test_default(self):
        project = get_project({})
        assert isinstance(project, DefaultProject)
        assert project.runner is None
        assert project.loaders == []
        assert project.workers == {}

        # An empty conf creates a name by default
        assert project.name == 'Unnamed project'

    def test_custom_project(self):
        project = get_project({
            'project': MyProject,
            'name': 'My Project'
        })
        assert isinstance(project, MyProject)
        assert project.name == 'My Project'

    def test_custom_project_wrong_class(self):
        with pytest.raises(TypeError) as exc:
            get_project({'project': object})
        assert str(exc.value) == (
            "A Project factory needs a `horsebox.types.Project` subclass."
        )

    def test_custom_project_check_config_fail(self):
        with pytest.raises(KeyError) as exc:
            get_project({'project': MyProject})
        assert str(exc.value) == (
            "'Expecting key `name` with a str type value.'"
        )


class TestRunner:

    def test_wrong_config_path(self):
        from minicli import run

        with pytest.raises(FileNotFoundError):
            run('run', 'toto')

    def test_config_path(self, config_file):
        from minicli import run
        run('run', str(config_file))

    def test_wrong_logging_level(self, capsys, config_file):
        from minicli import run

        with pytest.raises(SystemExit) as exc:
            run('run', str(config_file), '-l', 'something')

        out, err = capsys.readouterr()
        assert (
            "invalid choice: 'something' (choose from "
            "'critical', 'error', 'warning', 'info', 'debug')"
        ) in err
