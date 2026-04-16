from unittest import TestCase
from unittest.mock import (
    patch,
    mock_open,
    Mock,
    MagicMock,
    create_autospec,
    sentinel,
)

from pathlib import Path as _PathClass

import warnings

from ..toml import (
    TomlSource,
    EmptyConfigDict,
    _load_toml,
    _load_toml_file,
    _missing_file_handlers,
    _import_toml_load_function,
    _TOML_IMPORT_ERROR_MSG,
    Path,
    __getattr__,
)


SRC = 'batconf.sources.toml'

EXAMPLE_ENVIRONMENTS_TOML = """
[batconf]
default_env = 'test'

[test]
[test.bat]
key = 'value'
dict = {'not' = 'supported'}

[test.bat.remote_host]
api_key = 'example_api_key'
url = 'https://api-example.host.io/'

[alt.bat.module]
key = 'alt_value'
"""

EXAMPLE_SECTIONS_TOML = """
root_key = 'root value'

[section7]
k7 = 'v7'
[section9]
k9 = 'v9'
"""

EXAMPLE_FLAT_TOML = """
k0 = 'v0'
k1 = 'v1'
"""

# Required for python < 3.11
# These values are checked against toml/lib.loads method in integration tests
LOADED_ENV_DICT: dict = {
    'batconf': {'default_env': 'test'},
    'test': {
        'bat': {
            'key': 'value',
            'dict': {'not': 'supported'},
            'remote_host': {
                'api_key': 'example_api_key',
                'url': 'https://api-example.host.io/',
            },
        }
    },
    'alt': {'bat': {'module': {'key': 'alt_value'}}},
}
LOAD_SEC_DICT: dict = {
    'root_key': 'root value',
    'section7': {'k7': 'v7'},
    'section9': {'k9': 'v9'},
}
LOAD_FLAT_DICT: dict = {'k0': 'v0', 'k1': 'v1'}


# TODO: When python3.10 reaches EOL, switch to using tomllib.loads
# LOADED_ENV_DICT = loads(EXAMPLE_ENVIRONMENTS_TOML)
# LOADED_SEC_DICT = loads(EXAMPLE_SECTIONS_TOML)
# LOADED_FLAT_DICT = loads(EXAMPLE_FLAT_TOML)


class TomlSourceTests(TestCase):
    _load_toml: Mock

    def setUp(t):
        patches = [
            '_load_toml',
        ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t._load_toml.return_value = LOADED_ENV_DICT

        t.file_name = 'mock.config.toml'
        t.default_file_format = 'environments'
        t.default_missing_file_option = 'warn'

    def test___init__defaults(t):
        ts = TomlSource(
            file_path=t.file_name,
            # Default: file_format='environments',
            # Default: config_env=* loads default from file
            # Default: missing_file_option='warn',
        )

        t.assertEqual(ts._config_file_path, Path(t.file_name))
        # Enable multi-environment support by default
        t.assertEqual('environments', ts._file_format)

        t.assertEqual('test', ts._config_env)
        t.assertEqual(t.default_missing_file_option, ts._missing_file_option)

        t.assertDictEqual(ts._data, t._load_toml.return_value['test'])
        t._load_toml.assert_called_with(
            file_path=ts._config_file_path,
            when_missing=t.default_missing_file_option,
        )

        # When no env is specified, select the default from the config file
        t.assertEqual(
            LOADED_ENV_DICT['batconf']['default_env'],
            ts._config_env,
        )
        t.assertEqual(
            LOADED_ENV_DICT['test']['bat']['key'],
            ts.get('bat.key'),
        )

    def test__data_with_environments(t):
        ts = TomlSource(file_path=t.file_name)
        ts._config_env = 'new_config_env'
        env_cfg = {'k': 'v'}

        with t.subTest('defaults'):
            config = {ts._config_env: env_cfg}
            ts._data = config
            t.assertDictEqual(env_cfg, ts._data)

        with t.subTest('defaults: missing environment'):
            config = {'batconf': {'default_env': 'missing'}, 'v': env_cfg}
            with t.assertRaises(ValueError):
                ts._data = config

        with t.subTest('no config_env specified'):
            ts._config_env = None
            config = {'batconf': {'default_env': 'my_env'}, 'my_env': env_cfg}
            ts._data = config
            t.assertDictEqual(env_cfg, ts._data)

    def test__data_with_sections(t):
        ts = TomlSource(file_path=t.file_name, file_format='sections')
        sec_config = {'section0': {'k0': 'v0'}, 'section9': {'k9': 'v9'}}
        ts._data = sec_config

        t.assertIs(sec_config, ts._data)

    def test__data_with_flat_format(t):
        ts = TomlSource(file_path=t.file_name, file_format='flat')
        flat_config = {'k0': 'v0', 'k9': 'v9'}

        ts._data = flat_config

        t.assertIs(ts._data, flat_config)

    def test_get(t):
        """Trying to get a section value returns None, not a dict"""
        ts = TomlSource(file_path=t.file_name)

        t.assertIsNone(ts.get('bat'))
        t.assertIsNone(ts.get('bat.dict'))

    def test_get__from_env(t) -> None:
        ts = TomlSource(file_path=t.file_name)

        with t.subTest('single key'):
            t.assertEqual(
                ts.get('bat.key'),
                LOADED_ENV_DICT['test']['bat']['key'],
            )

        with t.subTest('key from module'):
            t.assertEqual(
                ts.get('api_key', path='bat.remote_host'),
                LOADED_ENV_DICT['test']['bat']['remote_host']['api_key'],
            )
        with t.subTest('missing item'):
            t.assertEqual(ts.get('_sir_not_appearing_in_this_film'), None)

    def test_get__from_sections(t):
        ts = TomlSource(file_path=t.file_name, file_format='sections')

        with t.subTest('defaults'):
            ts._data = LOAD_SEC_DICT
            t.assertEqual(ts.get('section7.k7'), 'v7')
            t.assertEqual(ts.get('section9.k9'), 'v9')
            t.assertEqual(ts.get('root_key'), 'root value')

        with t.subTest('missing section returns None'):
            t.assertIsNone(ts.get('section10'))

        with t.subTest('missing key returns None'):
            t.assertIsNone(ts.get('section0.k10'))

    def test_config_env_argument(t):
        ts = TomlSource('./example.config.toml', config_env='alt')
        t.assertEqual(
            LOADED_ENV_DICT['alt']['bat']['module']['key'],
            ts.get('key', path='bat.module'),
        )

    def test_missing_file_warning(t):
        """Default behavior.
        Missing config files result in a warning.
        And the loaded _data is empty
        """
        t._load_toml.return_value = EmptyConfigDict

        ts = TomlSource(file_path=t.file_name, missing_file_option='warn')

        t._load_toml.assert_called_with(
            file_path=ts._config_file_path,
            when_missing='warn',
        )
        t.assertIs(EmptyConfigDict, ts._data)
        t.assertIsNone(ts.get('bat.key'))

    def test_keys(t):
        ts = TomlSource(file_path=t.file_name)
        t.assertEqual(ts.keys(), {'bat': None}.keys())

    def test___str__(t) -> None:
        ts = TomlSource(file_path=t.file_name)
        t.assertEqual(f'Toml File: {repr(ts)}', str(ts))

    def test___repr__(t) -> None:
        ts = TomlSource(file_path=t.file_name)
        t.assertEqual(
            'TomlSource(file_path=mock.config.toml, config_env=test, '
            'missing_file_option=warn, file_format=environments)',
            repr(ts),
        )


class DeprecationTests(TestCase):
    def test_TomlConfig_returns_TomlSource(t):
        with warnings.catch_warnings(record=True):
            result = __getattr__('TomlConfig')
        t.assertIs(result, TomlSource)

    def test_TomlConfig_emits_deprecation_warning(t):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            __getattr__('TomlConfig')
        t.assertIs(w[0].category, DeprecationWarning)
        t.assertEqual(
            "'TomlConfig' is deprecated, use 'TomlSource' instead.",
            str(w[0].message),
        )


class TomlLoaderFunctionsTests(TestCase):
    _import_toml_load_function: Mock

    def setUp(t):
        # patch out tomllib.load
        patches = [
            '_import_toml_load_function',
        ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        # Patch out the pytoml module,
        # so tests can be run when it is not installed
        toml = MagicMock(spec=['loads', 'BaseLoader'])
        toml.loads.return_value = LOADED_ENV_DICT
        toml_patcher = patch.dict('sys.modules', {'toml': toml})
        t.toml = toml_patcher.start()
        t.addCleanup(toml_patcher.stop)

        # Patch out the `with open` statement, so it returns the mock_open obj
        t.m_open = mock_open(read_data=EXAMPLE_ENVIRONMENTS_TOML)
        open_patcher = patch('builtins.open', t.m_open)
        t.open = open_patcher.start()
        t.addCleanup(open_patcher.stop)

        t.loads = t._import_toml_load_function.return_value
        t.loads.return_value = LOADED_ENV_DICT
        t.file_path = _PathClass('./mock.config.toml')
        t.empy_config_dict = EmptyConfigDict

    def test__load_toml(t):
        """Test the _load_toml function default behavior"""
        ret = _load_toml(file_path=t.file_path, when_missing='error')
        t.open.assert_called_with(t.file_path, 'r')
        t.loads.assert_called_with(EXAMPLE_ENVIRONMENTS_TOML)
        t.assertEqual(ret, LOADED_ENV_DICT)

    @patch.dict(
        f'{SRC}._missing_file_handlers',
        warn=create_autospec(_missing_file_handlers['warn']),
        ignore=create_autospec(_missing_file_handlers['ignore']),
        error=create_autospec(_missing_file_handlers['error']),
    )
    def test__load_toml__when_missing_option(t):
        """Test that calling the _load_toml function
        with when_missing='error'
        calls the _load_file_error_when_missing function.
        """
        for opt in ('ignore', 'warn', 'error'):
            with t.subTest(f'when_missing={opt}'):
                ret = _load_toml(file_path=t.file_path, when_missing=opt)
                _missing_file_handlers[opt].assert_called_with(
                    loader_fn=_load_toml_file,
                    file_path=t.file_path,
                    empty_fallback=EmptyConfigDict,
                )
                t.assertIs(_missing_file_handlers[opt].return_value, ret)

    @patch(f'{SRC}._load_toml_file', autospec=True)
    def test__load_toml__FileNotFoundError(t, _load_toml_file: Mock):
        _load_toml_file.side_effect = FileNotFoundError

        with t.assertRaises(FileNotFoundError):
            _ = _load_toml(file_path=t.file_path, when_missing='error')

        _load_toml_file.assert_called_with(file_path=t.file_path)

    def test__load_toml_file(t):
        with t.subTest('file found'):
            ret = _load_toml_file(file_path=t.file_path)
            t.assertIs(ret, LOADED_ENV_DICT)
            t.open.assert_called_with(t.file_path, 'r')

        with t.subTest('missing file'):
            t.open.side_effect = FileNotFoundError
            with t.assertRaises(FileNotFoundError):
                _ = _load_toml_file(file_path=t.file_path)


class ImportTomlLoadFunctionTests(TestCase):
    _import_toml_load_function: Mock

    # patch out the pytoml module, as if it is not installed.
    @patch.dict('sys.modules', {'toml': None, 'tomllib': None})
    def test__import_toml_load_function_missing_toml_module(t):
        """The toml module is an optional extra,
        not required to use batconf after Python version 3.11.
        Using batconf without toml should not raise any Errors,
        But attempting to use TomlConfig when it is not installed
        will raise an ImportError on older versions of python without tomllib.
        """

        with t.subTest('pytoml behaves as if it is not installed'):
            with t.assertRaises(ImportError):
                from toml import load  # type: ignore  # noqa

        with t.subTest('Instantiating TomlSource raises ImportError'):
            with t.assertRaises(ImportError) as err:
                _ = _import_toml_load_function()

            t.assertEqual(err.exception.msg, _TOML_IMPORT_ERROR_MSG)

    @patch.dict(
        'sys.modules',
        {'tomllib': Mock(loads=sentinel.tomllib_load)},
        clear=True,
    )
    def test__import_toml_load_function_with_tomllib(t):
        load = _import_toml_load_function()
        t.assertIs(sentinel.tomllib_load, load)

    @patch.dict(
        'sys.modules',
        {'tomllib': None, 'toml': Mock(loads=sentinel.toml_load)},
        clear=True,
    )
    def test__import_toml_load_function_with_toml(t):
        load = _import_toml_load_function()
        t.assertIs(sentinel.toml_load, load)
