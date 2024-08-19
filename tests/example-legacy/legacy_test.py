from unittest import TestCase, skipIf
from unittest.mock import patch, Mock

from os import path, environ
from contextlib import contextmanager

from legacy import ProjectConfig
from legacy.conf import get_config
from legacy.lib import (
    hello_world,
    get_config_str,
    get_data_from_server,
)
from legacy.cli import BATCLI
from legacy.submodule import SubmoduleConfig
from legacy.submodule.sub import KEY2_DEFAULT


_PYYAML_INSTALLED = True
try:
    import yaml
except ImportError:
    _PYYAML_INSTALLED = False


# Get the absolute path to the test config.yaml file
example_dir = path.dirname(path.realpath(__file__))
config_file_name = path.join(example_dir, 'config.yaml')


@skipIf(not _PYYAML_INSTALLED, 'requires pyyaml')
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
            'Config.yaml: test.legacy.submodule.sub.key1',
        )

    def test_environment_variable(t):
        """Setting an environment variable, using the legacy namespace

        The environment variable name is the namespace-path to the cfg key
        All Uppercase, '_'(underscore) delimited.
        """
        value = 'Environment, value'
        override_value = 'overwrite key2 default'

        cfg = get_config(config_class=ProjectConfig)

        # Environment variables overwrite defaults from the Config class
        with set_environ('LEGACY_SUBMODULE_SUB_KEY2', override_value):
            t.assertEqual(cfg.submodule.sub.key2, override_value)

        # We have a limited ability to add new key:value pairs.
        # at this time, they must be added to existing namespaces
        with set_environ('LEGACY_SUBMODULE_ENVKEY', value):
            # environ["LEGACY_SUBMODULE_ENVKEY"] = value
            t.assertEqual(cfg.submodule.envkey, value)

        with t.assertRaises(AttributeError):
            # Unsupported arbitrary namespace
            with set_environ('LEGACY_SUBMODULE_UNKNOWN_KEY', value):
                # environ["LEGACY_SUBMODULE_UNKNOWN_KEY"] = value
                t.assertEqual(cfg.submodule.unknown.key, value)


class CLITests(TestCase):
    """
    Tests which invoke the project.cli.BATCLI *entry point*
    This is a bit of a shortcut to executing the CLI in a separate shell.
    """

    SRC = 'legacy.cli'

    @patch(f'{SRC}.exit', autospec=True)
    def test_hello_world(t, exit: Mock):
        ARGS = 'hello'.split(' ')

        with patch('builtins.print') as mock_print:
            BATCLI(ARGS=ARGS)

        mock_print.assert_called_with('Hello World!')
        exit.assert_called_once_with(0)


@skipIf(not _PYYAML_INSTALLED, 'requires pyyaml')
class LibTests(TestCase):
    def test_hello(t):
        ret = hello_world()
        t.assertEqual('Hello World!', ret)

    def test_get_config_str(t):
        t.assertRegex(
            get_config_str(),
            r"^legacy <class 'legacy.ProjectConfig'>:\n"
            r"    \|- submodule <class 'legacy\.submodule\.SubmoduleConfig'>:"
            r'\n'
            r'    \|    \|- sub <class'
            r" 'legacy\.submodule\.sub\.MyClient\.Config'>:\n"
            r'    \|    \|    \|- key1: "MISSING_VALUE"\n'
            r'    \|    \|    \|- key2: "DEFAULT VALUE"\n'
            r'SourceList=\[\n'
            r'    <batconf\.sources\.env\.EnvConfig object at .*>,\n'
            r'    <batconf\.sources\.file\.FileConfig object at .*>,\n'
            r'    <batconf\.sources\.dataclass\.DataclassConfig'
            r' object at .*>,\n'
            r'\]$',
        )

    def test_get_data_from_server(t):
        # This example has not set a default config file,
        # so we need to tell gitconfig where to find the test config file.
        ret = get_data_from_server(
            config_file_name=config_file_name,
        )
        t.assertEqual(
            "MyClient data: self.key1='Config.yaml:"
            " test.legacy.submodule.sub.key1', self.key2='DEFAULT VALUE'",
            ret,
        )


@contextmanager
def set_environ(key: str, value: str):
    try:
        environ[key] = value
        yield
    finally:
        del environ[key]
