from unittest import TestCase
from unittest.mock import (
    patch,
    mock_open,
    Mock,
    MagicMock,
    PropertyMock,
    create_autospec,
)

from pathlib import Path as _PathClass

from ..yaml import (
    YamlConfig,
    get_file_path,
    _load_yaml,
    _load_yaml_file,
    _empty_yaml_config,
    _missing_file_handlers,
    _missing_config_warning,
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

EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS = """
bat:
    key: envless_value
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

EXAMPLE_CONFIG_WITHOUT_ENV_DICT = {'bat': {'key': 'envless_value'}}
DEFAULT_EMPTY_CONFIGFILE_DICT = {'default': 'none', 'none': {}}


class YamlConfigTests(TestCase):
    get_file_path: Mock
    _load_yaml: Mock

    def setUp(t):
        patches = [
            'get_file_path',
            '_load_yaml',
        ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t._load_yaml.return_value = EXAMPLE_CONFIG_DICT

        t.config_file_name = 'example.config.yaml'
        t.default_missing_file_option = 'warn'

        t.yc = YamlConfig(config_file_name=t.config_file_name)

    def test___init__(t):
        t.assertEqual(t.yc._missing_file_option, t.default_missing_file_option)
        t.get_file_path.assert_called_with(
            file_name=t.config_file_name,
            when_missing=t.default_missing_file_option,
        )
        t._load_yaml.assert_called_with(
            file_path=t.yc._config_file_path,
            when_missing=t.default_missing_file_option,
        )
        t.assertEqual(
            EXAMPLE_CONFIG_DICT['example']['bat']['key'],
            t.yc.get('bat.key'),
        )
        # When no env is specified, select the default from the config file
        t.assertEqual(EXAMPLE_CONFIG_DICT['default'], t.yc._config_env)
        # Enable multi-environment support by default
        t.assertEqual(True, t.yc._enable_config_environments)

    def test__data(t):
        t.yc._config_env = 'new_config_env'
        env_cfg = {'k': 'v'}

        with t.subTest('defaults'):
            config = {t.yc._config_env: env_cfg}
            t.yc._data = config
            t.assertDictEqual(env_cfg, t.yc._data)

        with t.subTest('defaults: missing environment'):
            config = {'missing_environment': env_cfg}
            with t.assertRaises(KeyError):
                t.yc._data = config

        with t.subTest('no config_env specified'):
            t.yc._config_env = None
            config = {'default': 'my_env', 'my_env': env_cfg}
            t.yc._data = config
            t.assertDictEqual(env_cfg, t.yc._data)

        with t.subTest('config environments disabled'):
            yc = YamlConfig(
                config_file_name=t.config_file_name,
                enable_config_environments=False,
            )
            yc._data = env_cfg
            t.assertDictEqual(env_cfg, yc._data)

    def test__file_format(t):
        t.assertEqual('environments', t.yc._file_format)

        with t.subTest('config environments disabled'):
            yc_no_envs = YamlConfig(
                config_file_name=t.config_file_name,
                enable_config_environments=False,
            )
            t.assertEqual('sections', yc_no_envs._file_format)

    def test_disable_config_environments(t):
        """The default behavior for the configuration file allows it to
        contain separate configurations for different environments.
        This behavior may be disabled if desired.
        """
        t._load_yaml.return_value = EXAMPLE_CONFIG_WITHOUT_ENV_DICT

        yc = YamlConfig(
            config_file_name=t.config_file_name,
            enable_config_environments=False,
        )

        t.assertEqual(
            EXAMPLE_CONFIG_WITHOUT_ENV_DICT['bat']['key'],
            yc.get('bat.key'),
        )

    def test_get(t) -> None:
        conf = YamlConfig(config_file_name=t.config_file_name)

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

    @patch.object(YamlConfig, '_data', new_callable=PropertyMock)
    def test_loads_given_config_file(t, _data_prop: Mock):
        filename = './test_example.config.yaml'
        _ = YamlConfig(config_file_name=filename)
        # The loaded data is sent to the _data property setter
        _data_prop.assert_called_with(t._load_yaml.return_value)

        t.get_file_path.assert_called_with(
            file_name=filename,
            when_missing='warn',
        )
        pth = t.get_file_path.return_value
        t._load_yaml.assert_called_with(
            file_path=pth,
            when_missing=t.default_missing_file_option,
        )

    def test_config_env_argument(t):
        yc = YamlConfig('./example.config.yaml', config_env='alt')
        t.assertEqual(
            EXAMPLE_CONFIG_DICT['alt']['bat']['module']['key'],
            yc.get('key', module='bat.module'),
        )

    def test_missing_file_warning(t):
        """Default behavior.
        Missing config files result in a warning.
        """
        t._load_yaml.return_value = DEFAULT_EMPTY_CONFIGFILE_DICT

        yc = YamlConfig(
            config_file_name=t.config_file_name, missing_file_option='warn'
        )

        t._load_yaml.assert_called_with(
            file_path=yc._config_file_path,
            when_missing='warn',
        )
        t.assertDictEqual({}, yc._data)
        t.assertEqual(None, yc.get('bat.key'))

    def test__getitem__(t):
        yc = YamlConfig(config_file_name=t.config_file_name)

        with t.subTest('dot notation key path'):
            t.assertEqual(yc['bat.remote_host.api_key'], 'example_api_key')
        with t.subTest('__getitem__ chain'):
            t.assertEqual(
                yc['bat']['remote_host']['url'], 'https://api-example.host.io/'
            )

    def test_keys(t):
        yc = YamlConfig(config_file_name=t.config_file_name)
        t.assertEqual({'bat': None}.keys(), yc.keys())

    def test___str__(t) -> None:
        yc = YamlConfig(config_file_name=t.config_file_name)
        t.assertEqual(f'Yaml File: {repr(yc)}', str(yc))

    def test___repr__(t) -> None:
        yc = YamlConfig(config_file_name=t.config_file_name)
        t.assertEqual(
            f'YamlConfig(file_path={t.get_file_path.return_value}, '
            f'config_env=example, missing_file_option=warn, '
            f'file_format=environments)',
            repr(yc),
        )


class get_file_pathTests(TestCase):
    Path: Mock

    def setUp(t):
        t.extant_file = MagicMock(spec=_PathClass, name='extant_file')
        t.extant_file.is_file.return_value = True

        t.relative_file = MagicMock(spec=_PathClass, name='relative_file')
        t.relative_file.is_file.return_value = False
        t.relative_path = MagicMock(spec=_PathClass, name='relative_path')
        t.relative_file.resolve.return_value = t.relative_path
        t.relative_path.is_file.return_value = True

        t.missing_file = MagicMock(spec=_PathClass, name='missing_file')
        t.missing_file.is_file.return_value = False
        t.missing_file.resolve.return_value.is_file.return_value = False

        patches = [
            'Path',
        ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        # Default to a file that does exist
        t.Path.return_value = t.extant_file
        t.config_file_name = 'example.config.yaml'

    @patch(f'{SRC}.log', autospec=True)
    def test_missing_warning(t, log: Mock):
        """file path does not exist,
        default=warn
        """
        # When we call 'Path' on the file_name,
        # it returns a path to a file which is missing
        t.Path.return_value = t.missing_file
        pth = get_file_path(file_name=t.config_file_name)

        log.warning.assert_called_with(_missing_config_warning)
        t.assertIs(pth, t.missing_file)

    def test_missing_error(t):
        """
        file path does not exist, missing_file_option="error"
        Setting _config_file_name to an invalid path
        should raise a FileNotFound error
        """
        t.Path.return_value = t.missing_file

        with t.assertRaises(FileNotFoundError):
            _ = get_file_path(
                file_name=t.config_file_name,
                when_missing='error',
            )

    def test_missing_ignore(t):
        t.Path.return_value = t.missing_file
        pth = get_file_path(
            file_name=t.config_file_name,
            when_missing='ignore',
        )

        t.assertIs(pth, t.missing_file)

    def test_absolute_path(t):
        """when the absolute path exists, return it"""
        pth = get_file_path(file_name=t.config_file_name)
        t.assertIs(pth, t.extant_file)

    def test_relative_path(t):
        """When the relative path exists, return it"""
        t.Path.return_value = t.relative_file
        pth = get_file_path(file_name=t.config_file_name)
        # The relative_file has been saved to _config_file_path
        t.assertIs(pth, t.relative_path)


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
                    empty_fallback=_empty_yaml_config,
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
        But attempting to use YamlConfig when it is not installed
        will raise an ImportError."""

        with t.subTest('pyyaml behaves as if it is not installed'):
            with t.assertRaises(ImportError):
                import yaml  # noqa: quiet flake8

        with t.subTest('Instantiating YamlConfig raises ImportError'):
            with t.assertRaises(ImportError) as err:
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
