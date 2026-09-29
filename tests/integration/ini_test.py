from unittest import TestCase
from unittest.mock import patch, Mock

from os import path

from batconf.sources.ini import IniSource
from batconf.types import FILE_FORMATS


class IniSourceIntegrationTests(TestCase):
    def setUp(t):
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_ini_file_source_defaults(t):
        """Test the Default behavior of the IniSource configuration source"""
        t.config_file_path = path.join(t.this_dir, 'data/envs.config.ini')
        ins = IniSource(file_path=t.config_file_path)

        # selects default environment from the config file
        # get a value from the root of the default environment
        t.assertEqual('our testing environment', ins.get('doc'))
        # get a deeply nested value, from the default environment
        t.assertEqual(
            'envs.config.ini: test.project.submodule.sub.key1',
            ins.get('project.submodule.sub.key1'),
        )
        # getting a section returns None
        t.assertIsNone(ins.get('test.project.submodule'))

    def test_section_file(t):
        """Section files have no environment parameter,
        all sections of the file are available.
        """
        t.config_file_path = path.join(t.this_dir, 'data/sections.config.ini')
        ins = IniSource(file_path=t.config_file_path, file_format='sections')

        # Sections allow values to be nested by their path
        t.assertEqual(
            ins.get('sec0.sub0.value0'),
            'sections.config.ini :: sec0.sub0 :: value0',
        )
        # a key at the root of the file lives in the [/ROOT/] section
        t.assertEqual('is a valid key', ins.get('a_root_value'))
        # getting a section returns None
        t.assertIsNone(ins.get('sec1'))

    def test_flat_file(t):
        t.config_file_path = path.join(t.this_dir, 'data/flat.config.ini')
        ins = IniSource(file_path=t.config_file_path, file_format='flat')

        # all keys are root values
        t.assertEqual('value 0', ins.get('value0'))
        t.assertEqual('0', ins.get('int'))
        # undefined values return None
        t.assertIsNone(ins.get('undefined-key'))
        # keys may have .'s in them, to simulate nested paths
        t.assertEqual('still a root value', ins.get('not.really.nested'))
        # root is a valid key, in spite of the default section name
        t.assertEqual('is a valid key', ins.get('root'))


class IniSourceMissingFileTests(TestCase):
    """Test configurable behavior when the specified config file is missing."""

    def setUp(t):
        t.filename = 'sir.not.appearing.in.this.film'

    @patch('batconf.sources.file.log', autospec=True)
    def test_warning_default(t, log: Mock):
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                ins = IniSource(
                    file_path=t.filename,
                    file_format=file_format,
                )
                t.assertIsNone(ins.get('root'))
                log.warning.assert_called_with(
                    f'Config file not found: {t.filename}'
                )
                t.assertIsNone(ins.get('project.submodule.sub.key1'))
                t.assertIsNone(ins.get('any.random.key'))

    def test_missing_file_ignore(t):
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                ins = IniSource(
                    file_path=t.filename,
                    missing_file_option='ignore',
                    file_format=file_format,
                )
                t.assertIsNone(ins.get('doc'))
                t.assertIsNone(ins.get('project.submodule.sub.key1'))
                t.assertIsNone(ins.get('any.random.key'))
