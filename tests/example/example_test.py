from unittest import TestCase, skipIf
from unittest.mock import patch, Mock

from os import path, environ
from contextlib import contextmanager

from project.conf import get_config, ProjectConfigSchema, SubmoduleConfigSchema
from project.cli import BATCLI
from project.lib import (
    hello_world,
    get_data_from_server,
)
from project.submodule.client import KEY2_DEFAULT

from batconf.sources.yaml import YamlConfig


_PYYAML_INSTALLED = True
try:
    import yaml
except ImportError:
    _PYYAML_INSTALLED = False


# Get the absolute path to the test config.ini and .yaml files
example_dir = path.dirname(path.realpath(__file__))
ini_config_file_name = path.join(example_dir, 'config.ini')
yaml_config_file_name = path.join(example_dir, 'config.yaml')


class GetIniConfigFunctionTests(TestCase):
    def test_get_config(t):
        """Bare get_config() returns a Project-level Configuration object.
        Submodule configs can be accessed using their namespace.
        """
        cfg = get_config()
        # This cfg object can be used to lookup default values
        # provided by the Config dataclasses for the module.
        t.assertEqual(cfg.submodule.client.key2, KEY2_DEFAULT)

    def test_get_config_submodule(t):
        """Given A Config dataclass from a submodule,
        it returns a Configuration scoped to the module.

        .. versionchanged:: 0.2
           Free-form structured Configuration Schemas
           require the path parameter to be specified.
           Legacy behavior infered the path
           from the dataclass Schema's module.
        """
        cfg = get_config(
            config_class=SubmoduleConfigSchema, cfg_path='project.submodule'
        )
        t.assertEqual(cfg.client.key2, KEY2_DEFAULT)

        # Which can access values from structured Sources like ini files
        t.assertEqual(
            cfg.client.key1,
            'Config.ini: test.project.submodule.client.key1',
        )

    def test_reusable_configuration_schemas(t):
        """.. versionchanged:: 0.2
        Schemas can be reused inside of a parent schema.
        In this example, we demonstrate reusing the Client.Config Schema
        to provide configurations for multiple clients of the same type.
        """
        cfg = get_config()
        t.assertEqual(cfg.clients.clientA.key1, 'config.ini: clientA.key1')
        t.assertEqual(cfg.clients.clientB.key1, 'config.ini: clientB.key1')
        # Multiple sub-configs from the same Schema share default values
        t.assertEqual(cfg.clients.clientA.key2, KEY2_DEFAULT)
        t.assertEqual(cfg.clients.clientB.key2, KEY2_DEFAULT)

    def test_environment_variable(t):
        """Setting an environment variable, using the project namespace

        The environment variable name is the namespace-path to the cfg key
        All Uppercase, '_'(underscore) delimited.
        """
        value = 'Environment, value'
        override_value = 'overwrite key2 default'

        cfg = get_config(config_class=ProjectConfigSchema)

        # Environment variables overwrite defaults from the Config class
        with set_environ('PROJECT_SUBMODULE_CLIENT_KEY2', override_value):
            t.assertEqual(cfg.submodule.client.key2, override_value)

        # We have a limited ability to add new key:value pairs.
        # at this time, they must be added to existing namespaces
        with set_environ('PROJECT_SUBMODULE_ENVKEY', value):
            # environ["PROJECT_SUBMODULE_ENVKEY"] = value
            t.assertEqual(cfg.submodule.envkey, value)

        with t.assertRaises(AttributeError):
            # Unsupported arbitrary namespace
            with set_environ('PROJECT_SUBMODULE_UNKNOWN_KEY', value):
                # environ["PROJECT_SUBMODULE_UNKNOWN_KEY"] = value
                t.assertEqual(cfg.submodule.unknown.key, value)

    def test_args_variable(t):
        """
        Known Bug: github issue #67
          setting a key in ARGS will overwrite every key in the config with
          that name,
          .sources.args.CliArgsConfig does not recognize key paths.

          Note that both the nested and flat examples currently work.
          But they are both overwritten by setting just args.key2.
          To fix this but, we should distinguish between nested and flat
          configuration structures.
          Simply making CliArgsConfig path-aware may solve the problem.
        """
        from argparse import Namespace

        args = Namespace()
        args.key2 = 'cli override'

        cfg = get_config(cli_args=args)

        # Nested cfg example, with a key-path
        t.assertEqual(cfg.submodule.client.key2, 'cli override')
        # Flat cfg example, containing only key/value pairs
        t.assertEqual(cfg.key2, 'cli override')

    def test_args_path_based_variable(t):
        """
        Known Bug: github issue #67
          The current implementation of .sources.args.CliArgsConfig
          treats args as a flat structure.
          It does not recognize the full path of a key.
        """
        from argparse import Namespace

        args = Namespace()
        setattr(args, 'submodule.client.key2', 'path-based override')

        cfg = get_config(cli_args=args)

        # TODO: Fix this Bug
        # this check should not raise an error
        with t.assertRaises(AssertionError):
            t.assertEqual(
                cfg.submodule.client.key2,
                'path-based override',
            )


class CLITests(TestCase):
    """
    Tests which invoke the project.cli.BATCLI *entry point*
    This is a bit of a shortcut to executing the CLI in a separate shell.
    """

    SRC = 'project.cli'

    @patch(f'{SRC}.exit', autospec=True)
    def test_hello_world(t, exit: Mock):
        ARGS = 'hello'.split(' ')

        with patch('builtins.print') as mock_print:
            BATCLI(ARGS=ARGS)

        mock_print.assert_called_with('Hello World!')
        exit.assert_called_once_with(0)


class LibTests(TestCase):
    def test_hello_world(t):
        ret = hello_world()
        t.assertEqual('Hello World!', ret)

    def test_get_data_from_server(t):
        # This example has not set a default config file,
        # so we need to tell get_config where to find the test config file.
        ret = get_data_from_server()
        t.assertEqual(
            "MyClient data: self.key1='config.ini:"
            " clientB.key1', self.key2='DEFAULT VALUE'",
            ret,
        )

    def test_print_format(t):
        t.assertRegex(
            str(get_config()),
            (
                "Root <class 'project.ProjectConfigSchema'>:"
                "    |- submodule <class 'project.submodule.SubmoduleConfigSchema'>:"
                "    |    |- sub <class 'project.submodule.sub.MyClient.Config'>:"
                '    |    |    |- key1: "MISSING_VALUE"'
                '    |    |    |- key2: "DEFAULT VALUE"'
                'SourceList=['
                r'    <batconf.sources.env.EnvConfig object at 0x.*>,'
                r'    <batconf.sources.ini.IniConfig object at 0x.*>,'
                r'    <batconf.sources.dataclass.DataclassConfig object at 0x.*>,'
                ']'
            ),
        )


@contextmanager
def set_environ(key: str, value: str):
    try:
        environ[key] = value
        yield
    finally:
        del environ[key]


# Additional tests using a YamlConfig instead of IniConfig
@skipIf(not _PYYAML_INSTALLED, 'requires pyyaml')
class GetYamlConfigFunctionTests(TestCase):
    def setUp(t):
        # Inject a YamlConfig file source, to overwrite the default .ini
        t.yaml_config = YamlConfig(config_file_name=yaml_config_file_name)

    def test_get_config(t):
        """get_config() returns a Project-level Configuration object.

        Submodule configs can be accessed using their namespace.
        """
        # Inject a YamlConfig file source, to overwrite the default .ini
        cfg = get_config(config_file=t.yaml_config)
        # This cfg object can be used to lookup default values
        # provided by the Config dataclasses for the module.
        t.assertEqual(cfg.submodule.client.key2, KEY2_DEFAULT)

    def test_get_config_submodule(t):
        """Given A Config dataclass from a submodule,
        it returns a Configuration scoped to the module.

        .. versionchanged:: 0.2
           Free-form structured Configuration Schemas
           require the path parameter to be specified.
           Legacy behavior infered the path
           from the dataclass Schema's module.
        """
        cfg = get_config(
            config_class=SubmoduleConfigSchema,
            cfg_path='project.submodule',
            config_file=t.yaml_config,
        )
        t.assertEqual(cfg.client.key2, KEY2_DEFAULT)

        # Which can access values from structured Sources like yaml files
        t.assertEqual(
            cfg.client.key1,
            'Config.yaml: test.project.submodule.sub.key1',
        )

    def test_environment_variable(t):
        """Setting an environment variable, using the project namespace

        The environment variable name is the namespace-path to the cfg key
        All Uppercase, '_'(underscore) delimited.


        """
        value = 'Environment, value'
        override_value = 'overwrite key2 default'

        cfg = get_config(
            config_class=ProjectConfigSchema,
            config_file_name=yaml_config_file_name,
            config_file=t.yaml_config,
        )

        # Environment variables overwrite defaults from the Config class
        with set_environ('PROJECT_SUBMODULE_CLIENT_KEY2', override_value):
            t.assertEqual(cfg.submodule.client.key2, override_value)

        # We have a limited ability to add new key:value pairs.
        # at this time, they must be added to existing namespaces
        with set_environ('PROJECT_SUBMODULE_ENVKEY', value):
            # environ["PROJECT_SUBMODULE_ENVKEY"] = value
            t.assertEqual(cfg.submodule.envkey, value)

        with t.assertRaises(AttributeError):
            # Unsupported arbitrary namespace
            with set_environ('PROJECT_SUBMODULE_UNKNOWN_KEY', value):
                # environ["PROJECT_SUBMODULE_UNKNOWN_KEY"] = value
                t.assertEqual(cfg.submodule.unknown.key, value)

    def test_args_variable(t):
        """
        Known Bug: github issue #67
          setting a key in ARGS will overwrite every key in the config with
          that name,
          .sources.args.CliArgsConfig does not recognize key paths.

          Note that both the nested and flat examples currently work.
          But they are both overwritten by setting just args.key2.
          To fix this but, we should distinguish between nested and flat
          configuration structures.
          Simply making CliArgsConfig path-aware may solve the problem.
        """
        from argparse import Namespace

        args = Namespace()
        args.key2 = 'cli override'

        cfg = get_config(
            cli_args=args,
            config_file=t.yaml_config,
        )

        # Nested cfg example, with a key-path
        t.assertEqual(cfg.submodule.client.key2, 'cli override')
        # Flat cfg example, containing only key/value pairs
        t.assertEqual(cfg.key2, 'cli override')

    def test_args_path_based_variable(t):
        """
        Known Bug: github issue #67
          The current implementation of .sources.args.CliArgsConfig
          treats args as a flat structure.
          It does not recognize the full path of a key.
        """
        from argparse import Namespace

        args = Namespace()
        setattr(args, 'submodule.sub.key2', 'path-based override')

        cfg = get_config(
            cli_args=args,
            config_file=t.yaml_config,
        )

        # TODO: Fix this Bug
        # this check should not raise an error
        with t.assertRaises(AssertionError):
            t.assertEqual(
                cfg.submodule.client.key2,
                'path-based override',
            )
