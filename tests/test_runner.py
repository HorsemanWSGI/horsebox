import logging
import pytest
from horsebox.runner import get_project
from horsebox.types import Project
from horsebox.project import DefaultProject


class MyProject(Project):

    def __init__(self, logger):
        self.logger = logger

    def start(self):
        pass

    def stop(self):
        pass

    @classmethod
    def check_config(cls, config):
        if logger := config.get('logger'):
            if isinstance(logger, logging.Logger):
                return True
        raise KeyError(
            "Expecting key `logger` with an instance of "
            "`logging.Logger` as a value.")

    @classmethod
    def from_config(cls, config):
        cls.check_config(config)
        return cls(config['logger'])


class TestProjectExtraction:

    def test_default(self):
        project = get_project({})
        assert isinstance(project, DefaultProject)
        assert project.runner is None
        assert project.loaders == []
        assert project.workers == {}

        # An empty conf creates a logger by default
        assert project.logger is not None
        assert project.logger.name == 'Unnamed project'
        assert project.logger.level == logging.DEBUG

    def test_custom_project(self):
        project = get_project({
            'project': MyProject,
            'logger': logging.getLogger('My Project')
        })
        assert isinstance(project, MyProject)
        assert project.logger is not None
        assert project.logger.name == 'My Project'

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
            "'Expecting key `logger` with an instance of "
            "`logging.Logger` as a value.'"
        )
