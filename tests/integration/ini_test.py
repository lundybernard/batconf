from unittest import TestCase
from unittest.mock import patch

from os import path

from batconf.sources.ini import IniConfig, IniSource


class IniConfigIntegrationTests(TestCase):
    def setUp(t):
        # Get the absolute path to the test config.yaml file
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_ini_file_source_defaults(t):
        """Test the Default behavior of the IniConfig configuration source"""
        t.config_file_path = path.join(t.this_dir, 'data/envs.config.ini')
        ic = IniConfig(file_path=t.config_file_path)

        # selects default environment from the config file
        # get a value from the root of the default environment
        t.assertEqual('our testing environment', ic.get('doc'))
        # get a deeply nested value, from the default environment
        t.assertEqual(
            'envs.config.ini: test.project.submodule.sub.key1',
            ic.get('project.submodule.sub.key1'),
        )
        # getting a section returns None
        t.assertIsNone(ic.get('test.project.submodule'))

    def test_section_file(t):
        """Section files have no environment parameter,
        all sections of the file are available.
        """
        t.config_file_path = path.join(t.this_dir, 'data/sections.config.ini')
        ic = IniConfig(file_path=t.config_file_path, file_format='sections')

        # Sections allow values to be nested* by their path
        t.assertEqual(
            ic.get('sec0.sub0.value0'),
            'sections.config.ini :: sec0.sub0 :: value0',
        )
        # Section files require a section be specified for every get request
        t.assertIsNone(ic.get('a_root_value'))
        # getting a section returns None
        t.assertIsNone(ic.get('sec1'))

    def test_flat_file(t):
        t.config_file_path = path.join(t.this_dir, 'data/flat.config.ini')
        ic = IniConfig(file_path=t.config_file_path, file_format='flat')

        # all keys are root values
        t.assertEqual('value 0', ic.get('value0'))
        t.assertEqual('0', ic.get('int'))
        # undefined values return None
        t.assertIsNone(ic.get('undefined-key'))
        # keys may have .'s in them, to simulate nested paths
        t.assertEqual('still a root value', ic.get('not.really.nested'))
        # root is a valid key, in spite of the default section name
        t.assertEqual('is a valid key', ic.get('root'))


class IniConfigMissingFileTests(TestCase):
    """Test configurable behavior when the specified config file is missing."""

    def setUp(t):
        t.filename = 'sir.not.appearing.in.this.film'

    def test_warning_default(t):
        # The same behavior applies to all file formats
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                with patch('batconf.sources.file.log') as log:
                    ic = IniConfig(
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
                    _ = IniConfig(
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
                ic = IniConfig(
                    file_path=t.filename,
                    missing_file_option='ignore',
                    file_format=file_format,
                )

                # and all calls to .get will return None
                t.assertIsNone(ic.get('doc'))
                t.assertIsNone(ic.get('project.submodule.sub.key1'))
                t.assertIsNone(ic.get('any.random.key'))


class IniSourceIntegrationTests(TestCase):
    def setUp(t):
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_environments_file(t):
        """Default behavior: environments format reads the active environment."""
        config_file = path.join(t.this_dir, 'data/envs.config.ini')
        src = IniSource(file_path=config_file)

        # Selects the default environment from the config file.
        t.assertEqual('our testing environment', src.get('doc'))
        # Resolves deeply nested values within the active environment.
        t.assertEqual(
            'envs.config.ini: test.project.submodule.sub.key1',
            src.get('project.submodule.sub.key1'),
        )
        # A section path returns None, not a section dict.
        t.assertIsNone(src.get('test.project.submodule'))

    def test_environments_file_explicit_env(t):
        """config_env selects an environment other than the default."""
        config_file = path.join(t.this_dir, 'data/envs.config.ini')
        src = IniSource(file_path=config_file, config_env='production')

        t.assertEqual('Options for the production environment', src.get('doc'))

    def test_sections_file(t):
        """Sections format: all sections of the file are available."""
        config_file = path.join(t.this_dir, 'data/sections.config.ini')
        src = IniSource(file_path=config_file, file_format='sections')

        t.assertEqual(
            'sections.config.ini :: sec0.sub0 :: value0',
            src.get('sec0.sub0.value0'),
        )
        # Section files require a section for every get.
        t.assertIsNone(src.get('a_root_value'))
        # A section name alone returns None.
        t.assertIsNone(src.get('sec1'))

    def test_flat_file(t):
        config_file = path.join(t.this_dir, 'data/flat.config.ini')
        src = IniSource(file_path=config_file, file_format='flat')

        t.assertEqual('value 0', src.get('value0'))
        t.assertEqual('0', src.get('int'))
        t.assertIsNone(src.get('undefined-key'))
        t.assertEqual('still a root value', src.get('not.really.nested'))
        t.assertEqual('is a valid key', src.get('root'))


class IniSourceMissingFileTests(TestCase):
    """Test configurable behavior when the specified config file is missing."""

    def setUp(t):
        t.filename = 'sir.not.appearing.in.this.film'

    def test_warning_default(t):
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                with patch('batconf.sources.file.log') as log:
                    src = IniSource(
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
                    _ = IniSource(
                        file_path=t.filename,
                        missing_file_option='error',
                        file_format=file_format,
                    )

    def test_missing_file_ignore(t):
        """missing_file_option='ignore' silently returns None for all keys."""
        for file_format in ['environments', 'sections', 'flat']:
            with t.subTest(file_format=file_format):
                src = IniSource(
                    file_path=t.filename,
                    missing_file_option='ignore',
                    file_format=file_format,
                )
                t.assertIsNone(src.get('doc'))
                t.assertIsNone(src.get('project.submodule.sub.key1'))
                t.assertIsNone(src.get('any.random.key'))


class IniConfigDeprecationTests(TestCase):
    """IniConfig emits a DeprecationWarning on instantiation."""

    def test_deprecation_warning(t):
        with t.assertWarns(DeprecationWarning):
            _ = IniConfig(
                file_path='sir.not.appearing.in.this.film',
                missing_file_option='ignore',
            )
