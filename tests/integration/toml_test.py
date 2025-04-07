from unittest import TestCase, skipIf
from unittest.mock import patch

from os import path

from batconf.sources.toml import TomlConfig
from batconf.sources.tests.toml_test import (
    EXAMPLE_ENVIRONMENTS_TOML,
    LOADED_ENV_DICT,
    EXAMPLE_SECTIONS_TOML,
    LOAD_SEC_DICT,
    EXAMPLE_FLAT_TOML,
    LOAD_FLAT_DICT,
)

_TOML_INSTALLED = True
try:
    from tomllib import loads  # type: ignore  # noqa
except ImportError:
    try:
        from toml import loads  # type: ignore  # noqa
    except ImportError:
        _TOML_INSTALLED = False


@skipIf(not _TOML_INSTALLED, 'toml is not available, skipping')
class TomlUnittestStaticValuesTests(TestCase):
    """If toml support is available,
    use it to validate that our assumptions
    about how toml strings will be converted to dictionaries
    """

    def test_EXAMPLE_ENVIRONMENTS_TOML(t):
        loaded_dict = loads(EXAMPLE_ENVIRONMENTS_TOML)
        t.assertDictEqual(loaded_dict, LOADED_ENV_DICT)

    def test_EXAMPLE_SECTIONS_TOML(t):
        loaded_dict = loads(EXAMPLE_SECTIONS_TOML)
        t.assertDictEqual(loaded_dict, LOAD_SEC_DICT)

    def test_EXAMPLE_FLAT_TOML(t):
        loaded_dict = loads(EXAMPLE_FLAT_TOML)
        t.assertDictEqual(loaded_dict, LOAD_FLAT_DICT)


@skipIf(not _TOML_INSTALLED, 'toml is not available, skipping')
class TomlConfigIntegrationTests(TestCase):
    def setUp(t):
        # Get the absolute path to the test config.yaml file
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_toml_file_source_defaults(t):
        """Test the Default behavior of the TomlConfig configuration source"""
        t.config_file_path = path.join(t.this_dir, 'data/envs.config.toml')
        ic = TomlConfig(file_path=t.config_file_path)

        # selects default environment from the config file
        # get a value from the root of the default environment
        t.assertEqual('our testing environment', ic.get('doc'))
        # get a deeply nested value, from the default environment
        t.assertEqual(
            'envs.config.toml: test.project.submodule.sub.key1',
            ic.get('project.submodule.sub.key1'),
        )
        # getting a section returns None
        t.assertIsNone(ic.get('test.project.submodule'))

    def test_section_file(t):
        """Section files have no environment parameter,
        all sections of the file are available.
        """
        t.config_file_path = path.join(t.this_dir, 'data/sections.config.toml')
        ic = TomlConfig(file_path=t.config_file_path, file_format='sections')

        # Sections allow values to be "nested" by their path
        t.assertEqual(ic.get('section 001.section.name'), 'section 1')
        t.assertEqual(ic.get('section.9.key1'), 'val1')

        # Section files do support implicit root values without a section
        t.assertEqual(ic.get('a_root_value'), 'is a valid key')
        # getting a section returns None
        t.assertIsNone(ic.get('section 001'))
        t.assertIsNone(ic.get('section.7'))

    def test_flat_file(t):
        t.config_file_path = path.join(t.this_dir, 'data/flat.config.toml')
        ic = TomlConfig(file_path=t.config_file_path, file_format='flat')

        # all keys are root values
        t.assertEqual(ic.get('key0'), 'value0')
        t.assertEqual(ic.get('int'), '0')
        # undefined values return None
        t.assertIsNone(ic.get('undefined-key'))
        # keys may have .'s in them, to simulate nested paths
        t.assertEqual(ic.get('not.really.nested'), 'still a root value')
        # root is a valid key, in spite of the default section name
        t.assertEqual(ic.get('root'), 'is a valid key')


@skipIf(not _TOML_INSTALLED, 'toml is not available, skipping')
class TomlConfigMissingFileTests(TestCase):
    """Test configurable behavior when the specified config file is missing."""

    def setUp(t):
        t.filename = 'sir.not.appearing.in.this.film'

    def test_warning_default(t):
        # The same behavior applies to all file formats
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                with patch('batconf.sources.file.log') as log:
                    ic = TomlConfig(
                        file_path=t.filename,
                        file_format=file_format,
                        # missing_file_option='warning', is the default value
                    )
                    log.warning.assert_called_with(
                        f'Config file not found: {t.filename}'
                    )
                # and all calls to .get will return None
                t.assertIsNone(ic.get('root'))
                t.assertIsNone(ic.get('project.submodule.sub.key1'))
                t.assertIsNone(ic.get('any.random.key'))

    def test_missing_file_error(t):
        """when missing_file_option='error'
        attempting to load a missing file will raise a FileNotFoundError
        """
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                with t.assertRaises(FileNotFoundError):
                    _ = TomlConfig(
                        file_path=t.filename,
                        missing_file_option='error',
                        file_format=file_format,
                    )

    def test_missing_file_ignore(t):
        """when missing_file_option='ignore'
        attempting to load a missing file will not raise an error
        """
        file_formats = ['environments', 'sections', 'flat']
        for file_format in file_formats:
            with t.subTest(file_format=file_format):
                ic = TomlConfig(
                    file_path=t.filename,
                    missing_file_option='ignore',
                    file_format=file_format,
                )

                # and all calls to .get will return None
                t.assertIsNone(ic.get('doc'))
                t.assertIsNone(ic.get('project.submodule.sub.key1'))
                t.assertIsNone(ic.get('any.random.key'))
