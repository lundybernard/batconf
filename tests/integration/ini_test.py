from unittest import TestCase
from unittest.mock import patch

from os import path

from batconf.sources.ini import IniConfig


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
        t.assertEqual('s0s0v0', ic.get('sec0.sub0.value0'))
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


from batconf.manager import Configuration
from batconf.source import SourceList, SourceInterface
from typing import Optional, Sequence
from dataclasses import dataclass


class IniConfigConfigurationManagerTests(TestCase):
    """Test that IniConfig works as expected
    within the Configuration, and SourceList classes.
    """

    def test(t) -> None:
        this_dir = path.dirname(path.realpath(__file__))
        config_file_path = path.join(this_dir, 'data/envs.config.ini')
        ic = IniConfig(file_path=config_file_path)
        # Build a prioritized config source list
        config_sources: Sequence[Optional[SourceInterface]] = [ic, None]
        source_list = SourceList(config_sources)

        # Define a Configuration Schema
        @dataclass
        class SubmoduleSchema:
            key1: str
            key2: str = 'default from schema'

        # some horrible hacks, to force the __module__ lookup to work
        SubmoduleSchema.__module__ = 'project.submodule'

        @dataclass
        class CfgSchema:
            doc: str
            submodule: SubmoduleSchema

        CfgSchema.__module__ = 'project'

        cfg = Configuration(source_list, CfgSchema)
        print(cfg)
        # this should work, but requires the upcoming path changes
        t.assertEqual('project doc string', cfg.doc)

        t.assertEqual('wark', cfg.submodule.key2)
        t.assertEqual(
            'envs.config.ini: test.project.submodule.key1',
            cfg.submodule.key1,
        )

        print(f'{cfg.submodule=}')

        t.assertEqual('default from schema', cfg.submodule.key2)

        # Example fallback to key-lookup
        t.assertEqual('fallback', cfg.get('submodule.key1'))
