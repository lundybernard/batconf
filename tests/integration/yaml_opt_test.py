from unittest import TestCase, skipIf
from unittest.mock import patch

from os import path

from batconf.sources.yaml import YamlConfig
from batconf.sources.tests.yaml_test import (
    EXAMPLE_CONFIG_DICT,
    EXAMPLE_CONFIG_YAML,
    EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS,
    EXAMPLE_CONFIG_WITHOUT_ENV_DICT,
)

_PYYAML_INSTALLED = True
try:
    import yaml
except ImportError:
    _PYYAML_INSTALLED = False


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class SourcesYamlUnittestStaticValuesTests(TestCase):
    """If pyyaml is installed,
    use it to validate that our assumptions
    about how yaml strings will be converted to dictionaries
    """

    def test_EXAMPLE_CONFIG_DICT(t):
        loaded_dict = yaml.load(EXAMPLE_CONFIG_YAML, Loader=yaml.BaseLoader)
        t.assertDictEqual(EXAMPLE_CONFIG_DICT, loaded_dict)

    def test_EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS(t):
        loaded_envless_dict = yaml.load(
            EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS,
            Loader=yaml.BaseLoader,
        )
        t.assertDictEqual(EXAMPLE_CONFIG_WITHOUT_ENV_DICT, loaded_envless_dict)


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class YamlFileIntegrationTests(TestCase):
    def setUp(t):
        # Get the absolute path to the test config.yaml file
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_yaml_file_source_defaults(t):
        # Get the OS-agnostic absolute path to the test config.yaml file
        yml_config_file_name = path.join(t.this_dir, 'data', 'config.yaml')
        yc = YamlConfig(config_file_name=yml_config_file_name)

        t.assertEqual(
            'Config.yaml: test.project.submodule.sub.key1',
            yc.get('project.submodule.sub.key1'),
        )


@skipIf(not _PYYAML_INSTALLED, 'yaml is not available, skipping')
class YamlConfigMissingFileTests(TestCase):
    """Test configurable behavior when the specified config file is missing."""

    def setUp(t):
        t.filename = 'sir.not.appearing.in.this.film'

    def test_warning_default(t):
        # The same behavior applies to all file formats
        with patch('batconf.sources.yaml.log') as log:
            yc = YamlConfig(
                config_file_name=t.filename,
                # missing_file_option='warning', is the default value
            )
            log.warning.assert_called_with('Config File not found')
        # and all calls to .get will return None
        t.assertIsNone(yc.get('root'))
        t.assertIsNone(yc.get('project.submodule.sub.key1'))
        t.assertIsNone(yc.get('any.random.key'))

    def test_missing_file_error(t):
        """when missing_file_option='error'
        attempting to load a missing file will raise a FileNotFoundError
        """
        with t.assertRaises(FileNotFoundError):
            _ = YamlConfig(
                config_file_name=t.filename,
                missing_file_option='error',
            )

    def test_missing_file_ignore(t):
        """when missing_file_option='ignore'
        attempting to load a missing file will not raise an error
        """
        yc = YamlConfig(
            config_file_name=t.filename,
            missing_file_option='ignore',
        )

        # and all calls to .get will return None
        t.assertIsNone(yc.get('doc'))
        t.assertIsNone(yc.get('project.submodule.sub.key1'))
        t.assertIsNone(yc.get('any.random.key'))
