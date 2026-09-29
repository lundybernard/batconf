from unittest import TestCase
from unittest.mock import (
    patch,
    mock_open,
    Mock,
    MagicMock,
    create_autospec,
)

from pathlib import Path as _PathClass

from ..yaml import (
    YamlSource,
    ConfigEnvironmentNotFound,
    EmptyYamlDict,
    SourceDependencyNotFound,
    _load_yaml,
    _load_yaml_file,
    _missing_file_handlers,
    _YAML_IMPORT_ERROR_MSG,
)


SRC = 'batconf.sources.yaml'

EXAMPLE_CONFIG_YAML = """
default: example

example:
    bat:
        key: value
        remote_host:
            api_key: example_api_key
            url: https://api-example.host.io/

alt:
    bat:
        module:
            key: alt_value
"""

EXAMPLE_CONFIG_DICT: dict = {
    'default': 'example',
    'example': {
        'bat': {
            'key': 'value',
            'remote_host': {
                'api_key': 'example_api_key',
                'url': 'https://api-example.host.io/',
            },
        },
    },
    'alt': {'bat': {'module': {'key': 'alt_value'}}},
}

EXAMPLE_ENVIRONMENTS_DICT = {
    'batconf': {'default_env': 'example'},
    'example': {'bat': {'key': 'value', 'remote_host': {
        'api_key': 'example_api_key', 'url': 'https://api-example.host.io/'
    }}},
    'alt': {'bat': {'module': {'key': 'alt_value'}}},
}


class YamlSourceTests(TestCase):
    check_missing_file: Mock

    def setUp(t):
        patcher = patch(f'{SRC}._load_yaml', autospec=True)
        t._load_yaml = patcher.start()
        t.addCleanup(patcher.stop)

        patcher = patch(f'{SRC}.check_missing_file', autospec=True)
        t.check_missing_file = patcher.start()
        t.addCleanup(patcher.stop)

        t._load_yaml.return_value = EXAMPLE_ENVIRONMENTS_DICT
        t.ys = YamlSource(file_path='test.yaml')

    def test___init__(t):
        t._load_yaml.assert_not_called()  # lazy: file not read on construction
        t.assertEqual(t.ys._config_file_path, _PathClass('test.yaml'))
        t.check_missing_file.assert_called_with(
            file_path=_PathClass('test.yaml'),
            when_missing='warn',
        )
        t.assertEqual(t.ys._file_format, 'environments')
        t.assertEqual(t.ys._missing_file_option, 'warn')

        # Accessing _config_env triggers lazy load
        t.assertEqual(t.ys._config_env, 'example')
        t._load_yaml.assert_called_once_with(
            file_path=_PathClass('test.yaml'),
            when_missing='warn',
        )

    def test__data(t):
        """_raw_data is injected directly to bypass lazy file loading; tests _data's slicing logic."""
        with t.subTest('environments: reads batconf.default_env, extracts subtree'):
            env_cfg = {'k': 'v'}
            ys = YamlSource(file_path='test.yaml')
            ys.__dict__['_raw_data'] = {
                'batconf': {'default_env': 'test_env'},
                'test_env': env_cfg,
            }
            t.assertDictEqual(env_cfg, ys._data)
            t.assertEqual(ys._config_env, 'test_env')

        with t.subTest('environments: missing env is not found'):
            ys = YamlSource(file_path='test.yaml')
            ys.__dict__['_raw_data'] = {'batconf': {'default_env': 'missing'}}
            with t.assertRaises(ConfigEnvironmentNotFound):
                _ = ys._data

        with t.subTest('sections: returns raw dict'):
            raw = {'sec1': {'k': 'v'}}
            ys_s = YamlSource(file_path='test.yaml', file_format='sections')
            ys_s.__dict__['_raw_data'] = raw
            t.assertDictEqual(raw, ys_s._data)

        with t.subTest('flat: returns raw dict'):
            raw = {'key': 'val'}
            ys_f = YamlSource(file_path='test.yaml', file_format='flat')
            ys_f.__dict__['_raw_data'] = raw
            t.assertDictEqual(raw, ys_f._data)

        with t.subTest('EmptyYamlDict: stored as-is'):
            ys5 = YamlSource(file_path='test.yaml')
            ys5.__dict__['_raw_data'] = EmptyYamlDict
            t.assertIs(ys5._data, EmptyYamlDict)

    def test__config_env(t):
        with t.subTest('environments: populated from file default'):
            t.assertEqual(t.ys._config_env, 'example')

        with t.subTest('sections: always None'):
            t._load_yaml.return_value = {'sec': {}}
            ys_s = YamlSource(file_path='test.yaml', file_format='sections')
            t.assertIsNone(ys_s._config_env)

        with t.subTest('flat: always None'):
            t._load_yaml.return_value = {'k': 'v'}
            ys_f = YamlSource(file_path='test.yaml', file_format='flat')
            t.assertIsNone(ys_f._config_env)

    def test_get(t):
        with t.subTest('single key'):
            t.assertEqual(t.ys.get('bat.key'), 'value')

        with t.subTest('key with path'):
            t.assertEqual(
                t.ys.get('api_key', path='bat.remote_host'),
                'example_api_key',
            )

        with t.subTest('a dotted key under a path'):
            t.assertEqual(
                t.ys.get('remote_host.api_key', path='bat'),
                'example_api_key',
            )

        with t.subTest('missing key returns None'):
            t.assertIsNone(t.ys.get('nonexistent'))

        with t.subTest('dict node returns None'):
            t.assertIsNone(t.ys.get('bat'))

        with t.subTest('navigating past a leaf value returns None silently'):
            with t.assertNoLogs(SRC, 'WARNING'):
                t.assertIsNone(t.ys.get('bat.key.sub'))

    def test_keys(t):
        t.assertEqual(
            EXAMPLE_ENVIRONMENTS_DICT['example'].keys(),
            t.ys.keys(),
        )

    def test___str__(t):
        t.assertEqual(f'Yaml File: {repr(t.ys)}', str(t.ys))

    def test___repr__(t):
        t.assertEqual(
            f'YamlSource('
            f'file_path={_PathClass("test.yaml")}, '
            f'config_env=example, '
            f'missing_file_option=warn, '
            f'file_format=environments)',
            repr(t.ys),
        )

    def test_config_env_argument(t):
        ys = YamlSource(file_path='test.yaml', config_env='alt')
        t.assertEqual(ys.get('key', path='bat.module'), 'alt_value')


class YamlLoaderFunctionsTests(TestCase):
    def setUp(t):
        # Patch out the pyyaml module,
        # so tests can be run when it is not installed
        pyyaml = MagicMock(spec=['load', 'BaseLoader'])
        pyyaml.load.return_value = EXAMPLE_CONFIG_DICT
        pyyaml_patcher = patch.dict('sys.modules', {'yaml': pyyaml})
        t.pyyaml = pyyaml_patcher.start()
        t.addCleanup(pyyaml_patcher.stop)

        # Patch out the `with open` statement, so it returns the mock_open obj
        t.m_open = mock_open(read_data=EXAMPLE_CONFIG_YAML)
        open_patcher = patch('builtins.open', t.m_open)
        t.open = open_patcher.start()
        t.addCleanup(open_patcher.stop)

        t.file_path = _PathClass('./example.config.yaml')

    def test__load_yaml(t):
        """Default behavior: file is found and loaded."""
        ret = _load_yaml(file_path=t.file_path, when_missing='error')
        t.assertEqual(ret, EXAMPLE_CONFIG_DICT)

    @patch.dict(
        f'{SRC}._missing_file_handlers',
        warn=create_autospec(_missing_file_handlers['warn']),
        ignore=create_autospec(_missing_file_handlers['ignore']),
        error=create_autospec(_missing_file_handlers['error']),
    )
    def test__load_yaml__when_missing_option(t):
        """Dispatches to the correct handler with the right arguments."""
        for opt in ('warn', 'ignore', 'error'):
            with t.subTest(f'when_missing={opt}'):
                ret = _load_yaml(file_path=t.file_path, when_missing=opt)
                _missing_file_handlers[opt].assert_called_with(
                    loader_fn=_load_yaml_file,
                    file_path=t.file_path,
                    empty_fallback=EmptyYamlDict,
                )
                t.assertIs(_missing_file_handlers[opt].return_value, ret)

    @patch(f'{SRC}._load_yaml_file', autospec=True)
    def test__load_yaml__error(t, _load_yaml_file: Mock):
        _load_yaml_file.side_effect = FileNotFoundError

        with t.assertRaises(FileNotFoundError):
            _ = _load_yaml(file_path=t.file_path, when_missing='error')

        _load_yaml_file.assert_called_with(t.file_path)

    # patch out the pyyaml module, as if it is not installed.
    @patch.dict('sys.modules', {'yaml': None})
    def test__load_yaml_file_missing_pyyaml_module(t):
        """The pyyaml module is an optional extra,
        not required to use this package.
        Using the module without pyyaml should not raise any Errors,
        But attempting to use YamlSource when it is not installed
        will raise an ImportError."""

        with t.subTest('pyyaml behaves as if it is not installed'):
            with t.assertRaises(ImportError):
                import yaml  # noqa: quiet flake8

        with t.subTest('the pyyaml dependency is not found'):
            with t.assertRaises(SourceDependencyNotFound) as err:
                _ = _load_yaml_file(file_path=t.file_path)

            t.assertEqual(err.exception.msg, _YAML_IMPORT_ERROR_MSG)

    def test__load_yaml_file(t):
        with t.subTest('file found'):
            ret = _load_yaml_file(file_path=t.file_path)
            t.assertEqual(ret, EXAMPLE_CONFIG_DICT)
            t.open.assert_called_with(t.file_path)

        with t.subTest('missing file'):
            t.open.side_effect = FileNotFoundError
            with t.assertRaises(FileNotFoundError):
                _ = _load_yaml_file(file_path=t.file_path)


class YamlImportErrorMessageTests(TestCase):
    """_YAML_IMPORT_ERROR_MSG tells the user how to install pyyaml."""

    def test__YAML_IMPORT_ERROR_MSG(t):
        t.assertEqual(
            'PyYAML is required to use YamlSource. '
            'Please install it using `pip install pyyaml`. '
            'Or as an optional extra using `pip install batconf[yaml]`.',
            _YAML_IMPORT_ERROR_MSG,
        )
