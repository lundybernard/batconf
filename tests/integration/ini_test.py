from collections.abc import Iterator
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch, Mock

from os import path

from batconf.sources.ini import _IniConfig, IniSource
from batconf.types import FILE_FORMATS


@contextmanager
def _ini_file(text: str) -> Iterator[str]:
    """Yield the path of a temporary INI file that holds the text."""
    with TemporaryDirectory() as tmp_dir:
        file_path = path.join(tmp_dir, 'config.ini')
        with open(file_path, 'w') as cfg_file:
            cfg_file.write(text)
        yield file_path


class IniConfigIntegrationTests(TestCase):
    def setUp(t):
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_is_deprecated(t):
        import batconf.sources.ini as ini_module
        with t.assertWarns(DeprecationWarning) as cm:
            ini_module.__getattr__('IniConfig')
        t.assertEqual(
            "'IniConfig' is deprecated and will be removed in v0.5.0; "
            "use 'IniSource' instead.",
            str(cm.warning),
        )

    def test_ini_file_source_defaults(t):
        """Test the Default behavior of the IniConfig configuration source"""
        t.config_file_path = path.join(t.this_dir, 'data/envs.config.ini')
        ic = _IniConfig(file_path=t.config_file_path)

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
        ic = _IniConfig(file_path=t.config_file_path, file_format='sections')

        # Sections allow values to be nested by their path
        t.assertEqual(
            ic.get('sec0.sub0.value0'),
            'sections.config.ini :: sec0.sub0 :: value0',
        )
        # getting a section returns None
        t.assertIsNone(ic.get('sec1'))

    def test_flat_file(t):
        t.config_file_path = path.join(t.this_dir, 'data/flat.config.ini')
        ic = _IniConfig(file_path=t.config_file_path, file_format='flat')

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
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                with patch('batconf.sources.file.log') as log:
                    ic = _IniConfig(
                        file_path=t.filename,
                        file_format=file_format,
                        # missing_file_option='warning', is the default value
                    )
                    # and all calls to .get will return None
                    t.assertIsNone(ic.get('root'))
                    log.warning.assert_called_with(
                        f'Config file not found: {t.filename}'
                    )
                t.assertIsNone(ic.get('project.submodule.sub.key1'))
                t.assertIsNone(ic.get('any.random.key'))

    def test_missing_file_error(t):
        """when missing_file_option='error'
        attempting to load a missing file will raise a FileNotFoundError
        """
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                with t.assertRaises(FileNotFoundError):
                    ic = _IniConfig(
                        file_path=t.filename,
                        missing_file_option='error',
                        file_format=file_format,
                    )
                    ic.get('any_key')

    def test_missing_file_ignore(t):
        """when missing_file_option='ignore'
        attempting to load a missing file will not raise an error
        """
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                ic = _IniConfig(
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
        # getting a section returns None
        t.assertIsNone(ins.get('sec1'))

    def test_root_section(t):
        """A key outside every namespace reads from the [/ROOT/] section."""
        ins = IniSource(
            file_path=path.join(t.this_dir, 'data/sections.config.ini'),
            file_format='sections',
        )
        for root_path in (None, ''):
            with t.subTest(path=root_path):
                ret = ins.get('a_root_value', path=root_path)
                t.assertEqual('is a valid key', ret)

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

    def test_flat_file_sections(t):
        """A flat file reads the keys above its first section header."""
        later_header = 'host = localhost\n[server]\nport = 8080\n'
        root_header = 'host = localhost\n[root]\nport = 8080\n'
        cases = {
            'a key above a header': (later_header, 'host', 'localhost'),
            'a key under a header': (later_header, 'port', None),
            'a key above [root]': (root_header, 'host', 'localhost'),
            'a key under [root]': (root_header, 'port', None),
            'a [DEFAULT] key': (
                'host = localhost\n[DEFAULT]\nuser = admin\n',
                'user',
                'admin',
            ),
        }
        for name, (text, key, expected) in cases.items():
            with t.subTest(name), _ini_file(text) as file_path:
                ins = IniSource(file_path=file_path, file_format='flat')
                ret = ins.get(key)
                t.assertEqual(expected, ret)


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

    def test_missing_file_error(t):
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                with t.assertRaises(FileNotFoundError):
                    ins = IniSource(
                        file_path=t.filename,
                        missing_file_option='error',
                        file_format=file_format,
                    )
                    ins.get('any_key')

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
