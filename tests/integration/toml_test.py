import warnings
from unittest import TestCase, skipIf
from unittest.mock import patch, Mock

from os import path

from batconf.sources.toml import TomlSource
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
class TomlSourceIntegrationTests(TestCase):
    def setUp(t):
        # Get the absolute path to the test config.yaml file
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_toml_file_source_defaults(t):
        """Test the Default behavior of the TomlSource configuration source"""
        t.config_file_path = path.join(t.this_dir, 'data/envs.config.toml')
        ts = TomlSource(file_path=t.config_file_path)

        # selects default environment from the config file
        # get a value from the root of the default environment
        t.assertEqual('our testing environment', ts.get('doc'))
        # get a deeply nested value, from the default environment
        t.assertEqual(
            'envs.config.toml: test.project.submodule.sub.key1',
            ts.get('project.submodule.sub.key1'),
        )
        # getting a section returns None
        t.assertIsNone(ts.get('test.project.submodule'))

    def test_section_file(t):
        """Section files have no environment parameter,
        all sections of the file are available.
        """
        t.config_file_path = path.join(t.this_dir, 'data/sections.config.toml')
        ts = TomlSource(file_path=t.config_file_path, file_format='sections')

        # Sections allow values to be "nested" by their path
        t.assertEqual(ts.get('section 001.section.name'), 'section 1')
        t.assertEqual(ts.get('section.9.key1'), 'val1')

        # Section files do support implicit root values without a section
        t.assertEqual(ts.get('a_root_value'), 'is a valid key')
        # getting a section returns None
        t.assertIsNone(ts.get('section 001'))
        t.assertIsNone(ts.get('section.7'))

    def test_flat_file(t):
        t.config_file_path = path.join(t.this_dir, 'data/flat.config.toml')
        ts = TomlSource(file_path=t.config_file_path, file_format='flat')

        # all keys are root values
        t.assertEqual(ts.get('key0'), 'value0')
        t.assertEqual(ts.get('int'), '0')
        # undefined values return None
        t.assertIsNone(ts.get('undefined-key'))
        # keys may have .'s in them, to simulate nested paths
        t.assertEqual(ts.get('not.really.nested'), 'still a root value')
        # root is a valid key, in spite of the default section name
        t.assertEqual(ts.get('root'), 'is a valid key')


@skipIf(not _TOML_INSTALLED, 'toml is not available, skipping')
class TomlSourceMissingFileTests(TestCase):
    """Test configurable behavior when the specified config file is missing."""

    def setUp(t):
        t.filename = 'sir.not.appearing.in.this.film'

    @patch('batconf.sources.file.log', autospec=True)
    def test_warning_default(t, log: Mock):
        # The same behavior applies to all file formats
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                ts = TomlSource(
                    file_path=t.filename,
                    file_format=file_format,
                    # missing_file_option='warning', is the default value
                )
                log.warning.assert_called_with(
                    f'Config file not found: {t.filename}'
                )
            # and all calls to .get will return None
            t.assertIsNone(ts.get('root'))
            t.assertIsNone(ts.get('project.submodule.sub.key1'))
            t.assertIsNone(ts.get('any.random.key'))

    def test_missing_file_error(t):
        """when missing_file_option='error'
        attempting to load a missing file will raise a FileNotFoundError
        """
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                with t.assertRaises(FileNotFoundError):
                    _ = TomlSource(
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
                ts = TomlSource(
                    file_path=t.filename,
                    missing_file_option='ignore',
                    file_format=file_format,
                )

                # and all calls to .get will return None
                t.assertIsNone(ts.get('doc'))
                t.assertIsNone(ts.get('project.submodule.sub.key1'))
                t.assertIsNone(ts.get('any.random.key'))


class DeprecationTests(TestCase):
    def test_TomlConfig_is_a_deprecated_alias_for_TomlSource(t):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            from batconf.sources.toml import TomlConfig as tc

        # TomlConfig is an alias for TomlSource
        t.assertIs(tc, TomlSource)

        # Deprecation warning
        t.assertIs(w[0].category, DeprecationWarning)
        t.assertEqual(
            "'TomlConfig' is deprecated, use 'TomlSource' instead.",
            str(w[0].message)
        )
