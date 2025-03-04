from unittest import TestCase
from unittest.mock import patch, create_autospec, Mock, sentinel


from ..file import (
    # missing file handlers
    MissingFileHandlerP,
    load_file_warn_when_missing,
    load_file_ignore_when_missing,
    load_file_error_when_missing,
    # legacy FileConfig source
    FileConfig,
    load_config_file,
    os,
    Path,
    _missing_config_warning,
    _DEPRECATION_WARNING,
)


SRC = 'batconf.sources.file'


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


class FileLoaderFunctionTests(TestCase):
    def setUp(t):
        t.loader_fn = create_autospec(MissingFileHandlerP, spec_set=True)
        t.file_name = 'example.config.file'
        t.file_path = Path(t.file_name)

    def test_load_file_warn_when_missing(t):
        with t.subTest('file_path exists'):
            ret = load_file_warn_when_missing(
                loader_fn=t.loader_fn,
                file_path=t.file_path,
                empty_fallback=sentinel.EmptyConfig,
            )
            t.assertIs(t.loader_fn.return_value, ret)

        with t.subTest('file_path does not exist'):
            t.loader_fn.side_effect = FileNotFoundError

            with patch(f'{SRC}.log', autospec=True) as log:
                ret = load_file_warn_when_missing(
                    loader_fn=t.loader_fn,
                    file_path=t.file_path,
                    empty_fallback=sentinel.EmptyConfig,
                )
                log.warning.assert_called_with(
                    f'Config file not found: {t.file_name}',
                )
                t.assertEqual(ret, sentinel.EmptyConfig)
                t.loader_fn.assert_called_with(t.file_path)

    def test_load_file_ignore_when_missing(t):
        with t.subTest('file_path exists'):
            ret = load_file_ignore_when_missing(
                loader_fn=t.loader_fn,
                file_path=t.file_path,
                empty_fallback=sentinel.EmptyConfig,
            )
            t.assertIs(t.loader_fn.return_value, ret)

        with t.subTest('file_path does not exist'):
            t.loader_fn.side_effect = FileNotFoundError
            ret = load_file_ignore_when_missing(
                loader_fn=t.loader_fn,
                file_path=t.file_path,
                empty_fallback=sentinel.EmptyConfig,
            )
            t.assertEqual(ret, sentinel.EmptyConfig)
            t.loader_fn.assert_called_with(t.file_path)

    def test_load_file_error_when_missing(t):
        with t.subTest('file_path exists'):
            ret = load_file_error_when_missing(
                loader_fn=t.loader_fn,
                file_path=t.file_path,
            )
            t.assertIs(t.loader_fn.return_value, ret)

        with t.subTest('file_path does not exist'):
            t.loader_fn.side_effect = FileNotFoundError

            with t.assertRaises(FileNotFoundError):
                _ = load_file_error_when_missing(
                    loader_fn=t.loader_fn,
                    file_path=t.file_path,
                )


class TestFileConfig(TestCase):
    Path: Mock
    _load_yaml_file: Mock

    def setUp(t):
        patches = [
            'Path',
            '_load_yaml_file',
        ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t.Path.is_file.return_value = True
        t._load_yaml_file.return_value = EXAMPLE_CONFIG_DICT

    @patch(f'{SRC}.warn', autospec=True)
    def test_deprecation_warning(t, warn: Mock):
        _ = FileConfig()
        warn.assert_called_with(_DEPRECATION_WARNING)

    def test_get(t) -> None:
        conf = FileConfig()

        with t.subTest('single key'):
            t.assertEqual(
                conf.get('bat.key'),
                EXAMPLE_CONFIG_DICT['example']['bat']['key'],
            )

        with t.subTest('key from module'):
            t.assertEqual(
                conf.get('api_key', module='bat.remote_host'),
                EXAMPLE_CONFIG_DICT['example']['bat']['remote_host'][
                    'api_key'
                ],
            )
        with t.subTest('missing item'):
            t.assertEqual(conf.get('_sir_not_appearing_in_this_film'), None)

    def test_default_file(t):
        DEFAULT_FILE = '/config.yaml'

        _ = FileConfig()

        t._load_yaml_file.assert_called_with(
            file_path=t.Path(os.getcwd() + DEFAULT_FILE)
        )

    def test_loads_given_config_file(t):
        _ = FileConfig('./test_example.config.yaml', config_env='example')
        t._load_yaml_file.assert_called_with(t.Path.return_value)
        t.Path.assert_called_with('./test_example.config.yaml')

    def test_config_env_argument(t):
        t._load_yaml_file.return_value = EXAMPLE_CONFIG_DICT
        config_file = FileConfig('./example.config.yaml', config_env='alt')
        t._load_yaml_file.assert_called_with(t.Path.return_value)
        t.Path.assert_called_with('./example.config.yaml')
        t.assertEqual(config_file.get('key', module='bat.module'), 'alt_value')

    @patch.dict(f'{SRC}.os.environ', {}, clear=True)
    @patch(f'{SRC}.log', autospec=True)
    def test_missing_file(t, log):
        """No file found"""
        t.Path.return_value.is_file.return_value = False
        conf = FileConfig()
        log.warning.assert_called_with(_missing_config_warning)
        t.assertEqual(conf.get('_sir_not_appearing_in_this_film'), None)

    def test__getitem__(t):
        config_file = FileConfig()

        with t.subTest('dot notation key path'):
            t.assertEqual(
                config_file['bat.remote_host.api_key'], 'example_api_key'
            )
        with t.subTest('__getitem__ chain'):
            t.assertEqual(
                config_file['bat']['remote_host']['url'],
                'https://api-example.host.io/',
            )

    def test_keys(t):
        config_file = FileConfig()
        t.assertEqual(config_file.keys(), {'bat': None}.keys())


class Test_load_config_file(TestCase):
    _load_yaml_file: Mock

    def setUp(t):
        patches = [
            '_load_yaml_file',
        ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t._load_yaml_file.return_value = EXAMPLE_CONFIG_DICT

    def test_arg_config_file_name(t):
        conf = load_config_file('./example.config.yaml')

        t._load_yaml_file.assert_called_with(
            file_path=Path('example.config.yaml')
        )
        t.assertEqual(conf, EXAMPLE_CONFIG_DICT)

    def test_config_default_config_env(t):
        conf = load_config_file('./example.config.yaml')

        t.assertEqual(conf['default'], 'example')

        default_env = conf[conf['default']]

        t.assertEqual(default_env, conf['example'])

    @patch.dict(f'{SRC}.os.environ', {'BAT_CONFIG_FILE': 'env.config.yaml'})
    def test_config_file_env_variable(t):
        conf = load_config_file()

        t._load_yaml_file.assert_called_with(file_path=Path('env.config.yaml'))

        example_env = conf['example']['bat']
        t.assertEqual(example_env['remote_host']['api_key'], 'example_api_key')
        t.assertEqual(
            example_env['remote_host']['url'], 'https://api-example.host.io/'
        )

    @patch.dict(f'{SRC}.os.environ', {}, clear=True)
    def test_default_config_file(t):
        Path.is_file = create_autospec(
            Path.is_file, spec_set=True, return_value=True
        )

        CONF = load_config_file()

        t._load_yaml_file.assert_called_with(
            file_path=Path(os.getcwd() + '/config.yaml')
        )
        example_env = CONF['example']['bat']
        t.assertEqual(example_env['remote_host']['api_key'], 'example_api_key')
        t.assertEqual(
            example_env['remote_host']['url'], 'https://api-example.host.io/'
        )

    @patch.dict(f'{SRC}.os.environ', {}, clear=True)
    @patch(f'{SRC}.log', autospec=True)
    @patch(f'{SRC}.Path.is_file', autospec=True)
    def test_config_missing_file(t, path_is_file, log):
        """PROJECT_CONFIG is not set"""
        path_is_file.return_value = False
        conf = load_config_file()
        log.warning.assert_called_with(_missing_config_warning)
        t.assertEqual(conf['default'], 'none')
