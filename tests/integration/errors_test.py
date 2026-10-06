"""The public error contract.

A batconf failure is catchable as BatconfError, and stays catchable as
the standard exception it replaced.
"""
from unittest import TestCase

from dataclasses import dataclass
from os import path
from typing import cast

from batconf import (
    BatconfError,
    ConfigEnvironmentNotFound,
    ConfigFileNotFound,
    ConfigValueNotFound,
    Configuration,
    IniSource,
    InvalidFileFormat,
    SourceList,
)
from batconf.types import ConfigFileFormats


@dataclass
class ConfigSchema:
    nodefault: str
    value: str = 'schema default'


class ConfigurationErrorsTests(TestCase):
    def setUp(t) -> None:
        t.cfg = Configuration(
            source_list=SourceList([]),
            config_class=ConfigSchema,
            path='root',
        )

    def test_missing_value(t) -> None:
        with t.subTest('raises ConfigValueNotFound'):
            with t.assertRaises(ConfigValueNotFound):
                _ = t.cfg.nodefault

        with t.subTest('a BatconfError'):
            with t.assertRaises(BatconfError):
                _ = t.cfg.nodefault

        with t.subTest('still an AttributeError'):
            with t.assertRaises(AttributeError):
                _ = t.cfg.nodefault

        with t.subTest('getattr default still works'):
            t.assertEqual(getattr(t.cfg, 'nodefault', 'fallback'), 'fallback')


class FileSourceErrorsTests(TestCase):
    def setUp(t) -> None:
        t.data_dir = path.join(path.dirname(path.realpath(__file__)), 'data')
        t.config_file = path.join(t.data_dir, 'envs.config.ini')

    def test_missing_environment(t) -> None:
        ins = IniSource(file_path=t.config_file, config_env='no_such_env')

        with t.subTest('raises ConfigEnvironmentNotFound'):
            with t.assertRaises(ConfigEnvironmentNotFound):
                ins.get('doc')

        with t.subTest('a BatconfError'):
            with t.assertRaises(BatconfError):
                ins.get('doc')

        with t.subTest('still a ValueError'):
            with t.assertRaises(ValueError):
                ins.get('doc')

    def test_invalid_file_format(t) -> None:
        # the cast feeds the runtime guard a value the annotation forbids
        bad_format = cast(ConfigFileFormats, 'no_such_fmt')

        with t.subTest('raises InvalidFileFormat'):
            with t.assertRaises(InvalidFileFormat):
                IniSource(file_path=t.config_file, file_format=bad_format)

        with t.subTest('a BatconfError'):
            with t.assertRaises(BatconfError):
                IniSource(file_path=t.config_file, file_format=bad_format)

        with t.subTest('still a ValueError'):
            with t.assertRaises(ValueError):
                IniSource(file_path=t.config_file, file_format=bad_format)

    def test_missing_file(t) -> None:
        missing = path.join(t.data_dir, 'sir.not.appearing.in.this.film')

        with t.subTest('raises ConfigFileNotFound'):
            with t.assertRaises(ConfigFileNotFound):
                IniSource(file_path=missing, missing_file_option='error')

        with t.subTest('a BatconfError'):
            with t.assertRaises(BatconfError):
                IniSource(file_path=missing, missing_file_option='error')

        with t.subTest('still a FileNotFoundError'):
            with t.assertRaises(FileNotFoundError):
                IniSource(file_path=missing, missing_file_option='error')
