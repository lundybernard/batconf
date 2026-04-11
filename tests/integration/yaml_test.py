from unittest import TestCase, skipIf
from unittest.mock import patch

from os import path

from batconf.sources.yaml import YamlSource, YamlConfig
from batconf.sources.tests.yaml_test import (
    EXAMPLE_CONFIG_YAML,
    EXAMPLE_CONFIG_DICT,
    EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS,
    EXAMPLE_CONFIG_WITHOUT_ENV_DICT,
)

_PYYAML_INSTALLED = True
try:
    import yaml
except ImportError:
    _PYYAML_INSTALLED = False


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class YamlSourceUnittestStaticValuesTests(TestCase):
    """Validate that the unit-test YAML strings produce the expected dicts.

    Runs only when pyyaml is installed; ensures the constants imported from
    the unit-test module stay in sync with actual YAML parsing.
    """

    def test_EXAMPLE_CONFIG_DICT(t):
        loaded_dict = yaml.load(EXAMPLE_CONFIG_YAML, Loader=yaml.BaseLoader)
        t.assertDictEqual(EXAMPLE_CONFIG_DICT, loaded_dict)

    def test_EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS(t):
        loaded_dict = yaml.load(
            EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS,
            Loader=yaml.BaseLoader,
        )
        t.assertDictEqual(EXAMPLE_CONFIG_WITHOUT_ENV_DICT, loaded_dict)


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class YamlSourceIntegrationTests(TestCase):
    def setUp(t):
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_environments_file(t):
        """Default behavior: environments format reads the active environment."""
        config_file = path.join(t.this_dir, 'data/envs.config.yaml')
        src = YamlSource(file_path=config_file)

        # Selects the default environment from the config file.
        t.assertEqual('our testing environment', src.get('doc'))
        # Resolves deeply nested values within the active environment.
        t.assertEqual(
            'envs.config.yaml: test.project.submodule.sub.key1',
            src.get('project.submodule.sub.key1'),
        )
        # A path that resolves to a nested dict returns None, not the dict.
        t.assertIsNone(src.get('project.submodule'))

    def test_environments_file_explicit_env(t):
        """config_env selects an environment other than the default."""
        config_file = path.join(t.this_dir, 'data/envs.config.yaml')
        src = YamlSource(file_path=config_file, config_env='production')

        t.assertEqual(
            'Options for the production environment',
            src.get('doc'),
        )

    def test_sections_file(t):
        config_file = path.join(t.this_dir, 'data/sections.config.yaml')
        src = YamlSource(file_path=config_file, file_format='sections')

        t.assertEqual(
            'sections.config.yaml :: sec0.sub0 :: value0',
            src.get('sec0.sub0.value0'),
        )
        # A path that resolves to a nested dict returns None, not the dict.
        t.assertIsNone(src.get('sec1'))

    def test_flat_file(t):
        config_file = path.join(t.this_dir, 'data/flat.config.yaml')
        src = YamlSource(file_path=config_file, file_format='flat')

        t.assertEqual('value 0', src.get('value0'))
        t.assertEqual('0', src.get('int'))
        t.assertEqual('is a valid key', src.get('root'))
        t.assertIsNone(src.get('undefined-key'))


@skipIf(not _PYYAML_INSTALLED, 'yaml is not available, skipping')
class YamlSourceMissingFileTests(TestCase):
    """Test configurable behavior when the specified config file is missing."""

    def setUp(t):
        t.filename = 'sir.not.appearing.in.this.film'

    def test_warning_default(t):
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                with patch('batconf.sources.file.log') as log:
                    src = YamlSource(
                        file_path=t.filename,
                        file_format=file_format,
                    )
                    log.warning.assert_called_with(
                        f'Config file not found: {t.filename}'
                    )
                t.assertIsNone(src.get('root'))
                t.assertIsNone(src.get('project.submodule.sub.key1'))
                t.assertIsNone(src.get('any.random.key'))

    def test_missing_file_error(t):
        """missing_file_option='error' raises FileNotFoundError."""
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                with t.assertRaises(FileNotFoundError):
                    _ = YamlSource(
                        file_path=t.filename,
                        missing_file_option='error',
                        file_format=file_format,
                    )

    def test_missing_file_ignore(t):
        """missing_file_option='ignore' silently returns None for all keys."""
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                src = YamlSource(
                    file_path=t.filename,
                    missing_file_option='ignore',
                    file_format=file_format,
                )
                t.assertIsNone(src.get('doc'))
                t.assertIsNone(src.get('project.submodule.sub.key1'))
                t.assertIsNone(src.get('any.random.key'))


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class YamlConfigDeprecationTests(TestCase):
    """YamlConfig emits a DeprecationWarning on instantiation."""

    def test_deprecation_warning(t):
        with t.assertWarns(DeprecationWarning):
            _ = YamlConfig(
                config_file_name='sir.not.appearing.in.this.film',
                missing_file_option='ignore',
            )
