from unittest import TestCase, skipIf
from unittest.mock import patch, mock_open, Mock, MagicMock, PropertyMock

from pathlib import Path as _PathClass

from ..yaml import (
    YamlConfig,
    YamlSource,
    EmptyYamlConfig,
    warnings,
    get_file_path,
    _load_yaml,
    _load_yaml_source,
    _missing_file_handlers,
    _load_yaml_file_warn_when_missing,
    _load_yaml_file_ignore_when_missing,
    _load_yaml_file,
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
        # Suppress DeprecationWarning from YamlConfig across all tests in this
        # class; test_deprecation_warning covers the warning explicitly.
        _wm = warnings.catch_warnings()
        _wm.__enter__()
        t.addCleanup(_wm.__exit__, None, None, None)
        warnings.simplefilter('ignore', DeprecationWarning)

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

    @patch(f'{SRC}.warnings')
    def test_deprecation_warning(t, mock_warnings: Mock):
        """YamlConfig emits a DeprecationWarning pointing callers to YamlSource."""
        _ = YamlConfig(config_file_name=t.config_file_name)
        mock_warnings.warn.assert_called_once_with(
            'YamlConfig is deprecated, use YamlSource instead.'
            ' YamlConfig will be removed in a future release.',
            DeprecationWarning,
            stacklevel=2,
        )

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

    def test_loads_given_config_file(t):
        filename = './test_example.config.yaml'

        # some patch magic to mock the _data property
        with patch.object(
            YamlConfig, '_data', new_callable=PropertyMock
        ) as _data_prop:
            yc = YamlConfig(config_file_name=filename)
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
        yc._data = t._load_yaml.return_value

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
        t.empy_config_dict = {'default': 'none', 'none': {}}

    def test__load_yaml(t):
        ret = _load_yaml(file_path=t.file_path, when_missing='error')
        t.assertEqual(ret, EXAMPLE_CONFIG_DICT)

    def test__load_yaml_ignore(t):
        t.open.side_effect = FileNotFoundError  # this error will be ignored
        ret = _load_yaml(file_path=t.file_path, when_missing='ignore')
        t.assertEqual(ret, t.empy_config_dict)

    @patch(f'{SRC}._load_yaml_file_warn_when_missing', autospec=True)
    def test__load_yaml_warn(t, _load_yaml_file_warn_when_missing: Mock):
        ret = _load_yaml(file_path=t.file_path, when_missing='warn')
        _load_yaml_file_warn_when_missing.assert_called_with(
            file_path=t.file_path,
        )
        t.assertIs(_load_yaml_file_warn_when_missing.return_value, ret)

    @patch(f'{SRC}._load_yaml_file', autospec=True)
    def test__load_yaml_error(t, _load_yaml_file: Mock):
        _load_yaml_file.side_effect = FileNotFoundError
        with t.assertRaises(FileNotFoundError):
            _ = _load_yaml(file_path=t.file_path, when_missing='error')

        _load_yaml_file.assert_called_with(file_path=t.file_path)

    @patch(f'{SRC}.log', autospec=True)
    def test__load_yaml_file_warn_when_missing(t, log: Mock):
        """Logs a warning if the file is missing"""
        with t.subTest('file found'):
            ret = _load_yaml_file_warn_when_missing(file_path=t.file_path)
            t.assertEqual(ret, EXAMPLE_CONFIG_DICT)

        with t.subTest('file not found'):
            t.open.side_effect = FileNotFoundError

            ret = _load_yaml_file_warn_when_missing(file_path=t.file_path)

            t.open.assert_called_with(t.file_path)
            log.warning.assert_called_with(_missing_config_warning)
            t.assertEqual(ret, t.empy_config_dict)

    @patch(f'{SRC}.log', autospec=True)
    def test__load_yaml_file_ignore_when_missing(t, log):
        """Logs a warning if the file is missing"""
        with t.subTest('file found'):
            ret = _load_yaml_file_ignore_when_missing(file_path=t.file_path)
            t.assertEqual(ret, EXAMPLE_CONFIG_DICT)

        with t.subTest('file not found'):
            t.open.side_effect = FileNotFoundError

            ret = _load_yaml_file_ignore_when_missing(file_path=t.file_path)

            t.open.assert_called_with(t.file_path)
            log.warning.assert_not_called()
            t.assertEqual(ret, t.empy_config_dict)

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


class YamlSourceTests(TestCase):
    _load_yaml_source: Mock

    def setUp(t) -> None:
        patcher = patch(f'{SRC}._load_yaml_source', autospec=True)
        t._load_yaml_source = patcher.start()
        t.addCleanup(patcher.stop)

        t._load_yaml_source.return_value = EXAMPLE_CONFIG_DICT

        t.file_path = 'example.config.yaml'
        t.subject = YamlSource(file_path=t.file_path)

    def test___init__(t) -> None:
        t.assertEqual('warn', t.subject._missing_file_option)
        t.assertEqual('environments', t.subject._file_format)
        t._load_yaml_source.assert_called_with(
            file_path=t.subject._config_file_path,
            when_missing='warn',
        )
        # Default environment is read from the config dict.
        t.assertEqual(EXAMPLE_CONFIG_DICT['default'], t.subject._config_env)

    @patch(f'{SRC}.warnings')
    def test_no_deprecation_warning(t, mock_warnings: Mock) -> None:
        """YamlSource must not emit a DeprecationWarning."""
        _ = YamlSource(file_path=t.file_path)
        mock_warnings.warn.assert_not_called()

    def test__data(t) -> None:
        with t.subTest('environments: selects active env from config_env'):
            ys = YamlSource(file_path=t.file_path)
            ys._config_env = 'example'
            ys._data = {'example': {'k': 'v'}}
            t.assertDictEqual({'k': 'v'}, ys._data)

        with t.subTest('environments: reads default key when config_env is None'):
            ys = YamlSource(file_path=t.file_path)
            ys._config_env = None
            ys._data = {'default': 'my_env', 'my_env': {'k': 'v'}}
            t.assertDictEqual({'k': 'v'}, ys._data)
            t.assertEqual('my_env', ys._config_env)

        with t.subTest('environments: missing environment raises KeyError'):
            ys = YamlSource(file_path=t.file_path)
            ys._config_env = 'missing'
            with t.assertRaises(KeyError):
                ys._data = {'other': {}}

        with t.subTest('sections: stores the whole dict'):
            ys = YamlSource(file_path=t.file_path, file_format='sections')
            config = {'sec0': {'key': 'val'}}
            ys._data = config
            t.assertDictEqual(config, ys._data)

        with t.subTest('flat: stores the whole dict'):
            ys = YamlSource(file_path=t.file_path, file_format='flat')
            config = {'key': 'val'}
            ys._data = config
            t.assertDictEqual(config, ys._data)

        with t.subTest('empty sentinel passes through unchanged'):
            ys = YamlSource(file_path=t.file_path)
            ys._data = EmptyYamlConfig
            t.assertIs(EmptyYamlConfig, ys._data)

    def test__file_format_stored(t) -> None:
        """_file_format is a stored attribute, not a computed property."""
        for fmt in ('environments', 'sections', 'flat'):
            with t.subTest(file_format=fmt):
                ys = YamlSource(file_path=t.file_path, file_format=fmt)
                t.assertEqual(fmt, ys._file_format)

    def test_get(t) -> None:
        with t.subTest('single key'):
            t.assertEqual(
                EXAMPLE_CONFIG_DICT['example']['bat']['key'],
                t.subject.get('bat.key'),
            )

        with t.subTest('key with path argument'):
            t.assertEqual(
                EXAMPLE_CONFIG_DICT['example']['bat']['remote_host']['api_key'],
                t.subject.get('api_key', 'bat.remote_host'),
            )

        with t.subTest('missing key returns None'):
            t.assertIsNone(t.subject.get('_sir_not_appearing_in_this_film'))

        with t.subTest('result is a dict returns None'):
            # Unlike YamlConfig, YamlSource is consistent with Toml/IniSource.
            t.assertIsNone(t.subject.get('bat'))

    def test___str__(t) -> None:
        t.assertEqual(f'Yaml File: {repr(t.subject)}', str(t.subject))

    def test___repr__(t) -> None:
        t.assertEqual(
            f'YamlSource('
            f'file_path={t.subject._config_file_path}, '
            f'config_env={t.subject._config_env}, '
            f'missing_file_option={t.subject._missing_file_option}, '
            f'file_format={t.subject._file_format}'
            f')',
            repr(t.subject),
        )


class _load_yaml_sourceTests(TestCase):
    mock_missing_file_handlers = {
        'warn': Mock(spec=_missing_file_handlers['warn']),
        'ignore': Mock(spec=_missing_file_handlers['ignore']),
        'error': Mock(spec=_missing_file_handlers['error']),
    }

    @patch.dict(f'{SRC}._missing_file_handlers', mock_missing_file_handlers)
    def test__load_yaml_source(t) -> None:
        file_path = _PathClass('./example.config.yaml')
        for when_missing in ('warn', 'ignore', 'error'):
            with t.subTest(when_missing=when_missing):
                ret = _load_yaml_source(
                    file_path=file_path,
                    when_missing=when_missing,
                )
                _missing_file_handlers[when_missing].assert_called_with(
                    loader_fn=_load_yaml_file,
                    file_path=file_path,
                    empty_fallback=EmptyYamlConfig,
                )
                t.assertIs(_missing_file_handlers[when_missing].return_value, ret)
