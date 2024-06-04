from unittest import TestCase

from project import ProjectConfig
from project.conf import get_config
from project.submodule import SubmoduleConfig
from project.submodule.sub import KEY2_DEFAULT

from os import path, environ
from contextlib import contextmanager


# Get the absolute path to the test config.yaml file
example_dir = path.dirname(path.realpath(__file__))
config_file_name = path.join(example_dir, "config.yaml")


class GetConfigFunctionTests(TestCase):

    def test_get_config(t):
        """Bare get_config() returns a Project-level Configuration object.

        Submodule configs can be accessed using their namespace.
        """
        cfg = get_config()
        # This cfg object can be used to lookup default values
        # provided by the Config dataclasses for the module.
        t.assertEqual(cfg.submodule.sub.key2, KEY2_DEFAULT)

    def test_get_config_submodule(t):
        """Given A Config dataclass from a submodule,
        it returns a Configuration scoped to the module.
        """
        cfg = get_config(
            config_class=SubmoduleConfig,
            config_file_name=config_file_name,
        )
        t.assertEqual(cfg.sub.key2, KEY2_DEFAULT)

        # Which can access values from structured Sources like yaml files
        t.assertEqual(
            cfg.sub.key1,
            "Config.yaml: test.project.submodule.sub.key1",
        )

    def test_environment_variable(t):
        """Setting an environment variable, using the project namespace

        The environment variable name is the namespace-path to the cfg key
        All Uppercase, '_'(underscore) delimited.
        """
        value = "Environment, value"
        override_value = "overwrite key2 default"

        cfg = get_config(config_class=ProjectConfig)

        # Environment variables overwrite defaults from the Config class
        with set_environ("PROJECT_SUBMODULE_SUB_KEY2", override_value):
            t.assertEqual(cfg.submodule.sub.key2, override_value)

        # We have a limited ability to add new key:value pairs.
        # at this time, they must be added to existing namespaces
        with set_environ("PROJECT_SUBMODULE_ENVKEY", value):
            # environ["PROJECT_SUBMODULE_ENVKEY"] = value
            t.assertEqual(cfg.submodule.envkey, value)

        with t.assertRaises(AttributeError):
            # Unsupported arbitrary namespace
            with set_environ("PROJECT_SUBMODULE_UNKNOWN_KEY", value):
                # environ["PROJECT_SUBMODULE_UNKNOWN_KEY"] = value
                t.assertEqual(cfg.submodule.unknown.key, value)


@contextmanager
def set_environ(key: str, value: str):
    try:
        environ[key] = value
        yield
    finally:
        del environ[key]
