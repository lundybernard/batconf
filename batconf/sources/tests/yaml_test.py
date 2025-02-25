from unittest import TestCase
from unittest.mock import patch, mock_open, Mock, MagicMock, PropertyMock

import os
from pathlib import Path as _PathClass

from mypy.types import names

from ..file import load_config_file
from ..yaml import (
    YamlConfig,
    get_file_path,
    _load_yaml_file,
    _missing_config_warning,
)

import yaml


SRC = 'batconf.sources.yaml'


EXAMPLE_CONFIG_YAML = '''
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
'''

EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS = '''
bat:
    key: envless_value
'''

EXAMPLE_CONFIG_DICT = yaml.load(EXAMPLE_CONFIG_YAML, Loader=yaml.BaseLoader)
EXAMPLE_CONFIG_WITHOUT_ENV_DICT = yaml.load(
    EXAMPLE_CONFIG_WITHOUT_ENVIRONMENTS,
    Loader=yaml.BaseLoader,
)


class YamlConfigTests(TestCase):
    get_file_path: Mock
    _load_yaml_file: Mock

    def setUp(t):
        patches = ['get_file_path', '_load_yaml_file', ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t._load_yaml_file.return_value = EXAMPLE_CONFIG_DICT

        t.config_file_name = 'example.config.yaml'

    def test___init__(t):
        yc = YamlConfig(config_file_name=t.config_file_name)

        t.assertEqual(yc._missing_file_option, 'warn')
        t.get_file_path.assert_called_with(
            file_name=t.config_file_name,
            when_missing='warn',
        )
        # When no env is specified, select the default from the config file
        t.assertEqual(EXAMPLE_CONFIG_DICT['default'], yc._config_env)
        # Enable multi-environment support by default
        t.assertEqual(True, yc._enable_config_environments)




    def test_disable_config_environments(t):
        """The default behavior for the configuration file allows it to
        contain separate configurations for different environments.
        This behavior may be disabled if desired.
        """
        t._load_yaml_file.return_value = EXAMPLE_CONFIG_WITHOUT_ENV_DICT

        yc = YamlConfig(
            config_file_name=t.config_file_name,
            enable_config_environments=False,
        )

        t.assertEqual(
            EXAMPLE_CONFIG_WITHOUT_ENV_DICT['bat']['key'],
            yc.get('bat.key'),
        )

    def test_get(t) -> None:
        #with patch('builtins.open', t.m_open):
        conf = YamlConfig(config_file_name=t.config_file_name)

        with t.subTest('single key'):
            t.assertEqual(
                conf.get('bat.key'),
                EXAMPLE_CONFIG_DICT['example']['bat']['key']
            )

        with t.subTest('key from module'):
            t.assertEqual(
                conf.get('api_key', module='bat.remote_host'),
                EXAMPLE_CONFIG_DICT['example']['bat']['remote_host']['api_key']
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
            _data_prop.assert_called_with(t._load_yaml_file.return_value)

        t.get_file_path.assert_called_with(
            file_name=filename,
            when_missing='warn',
        )
        pth = t.get_file_path.return_value
        t._load_yaml_file.assert_called_with(file_path=pth)
        yc._data = t._load_yaml_file.return_value

    def test_config_env_argument(t):
        yc = YamlConfig(
            './example.config.yaml', config_env='alt'
        )
        t.assertEqual(
            EXAMPLE_CONFIG_DICT['alt']['bat']['module']['key'],
            yc.get('key', module='bat.module'),
        )

    def test_missing_file_allowed(t):
        '''Default behavior.
        Missing config files result in a warning.
        '''
        t._load_yaml_file.side_effect = FileNotFoundError

        yc = YamlConfig(config_file_name=t.config_file_name)

        t.assertEqual(yc.get('bat.key'), None)

    def test__getitem__(t):
        yc = YamlConfig(config_file_name=t.config_file_name)

        with t.subTest('dot notation key path'):
            t.assertEqual(
                yc['bat.remote_host.api_key'],
                'example_api_key'
            )
        with t.subTest('__getitem__ chain'):
            t.assertEqual(
                yc['bat']['remote_host']['url'],
                'https://api-example.host.io/'
            )

    def test_keys(t):
        yc = YamlConfig(config_file_name=t.config_file_name)
        t.assertEqual({'bat': None}.keys(), yc.keys())


class FileCheckerTests(TestCase):
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

        patches = ['Path', ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        # Default to a file that does exist
        t.Path.return_value = t.extant_file
        t.config_file_name = 'example.config.yaml'

    @patch(f'{SRC}.log', autospec=True)
    def test_missing_warning(t, log: Mock):
        '''file path does not exist,
        default=warn
        '''
        # When we call 'Path' on the file_name,
        # it returns a path to a file which is missing
        t.Path.return_value = t.missing_file
        pth = get_file_path(file_name=t.config_file_name)

        log.warning.assert_called_with(_missing_config_warning)
        t.assertIs(pth, t.missing_file)

    def test_missing_error(t):
        with t.subTest(
            'file path does not exist, missing_file_option="error"'
        ):
            '''Setting _config_file_name to an invalid path 
            should raise a FileNotFound error
            '''
            print('test__config_file_missing_error')
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
        '''when the absolute path exists, return it
        '''
        pth = get_file_path(file_name=t.config_file_name)
        t.assertIs(pth, t.extant_file)

    def test_relative_path(t):
        '''When the relative path exists, return it
        '''
        t.Path.return_value = t.relative_file
        pth = get_file_path(file_name=t.config_file_name)
        # The relative_file has been saved to _config_file_path
        t.assertIs(pth, t.relative_path)


class YamlLoaderTests(TestCase):
    def setUp(t):
        t.m_open = mock_open(read_data=EXAMPLE_CONFIG_YAML)

        open_patcher = patch('builtins.open', t.m_open)
        open_patcher.start()
        t.addCleanup(open_patcher.stop)

        t.file_path = _PathClass('./example.config.yaml')

    # patch out the pyyaml module, as if it is not installed.
    @patch.dict('sys.modules', {'yaml': None})
    def test_missing_pyyaml_module(t):
        """The pyyaml module is an optional extra,
         not requeired to use this package.
         Using the module without pyyaml should not raise any Errors,
         But attempting to use YamlConfig when it is not installed
         will raise an ImprortError.
         """

        with t.subTest('pyyaml behaves as if it is not installed'):
            with t.assertRaises(ImportError):
                import yaml

        with t.subTest('Instantiating YamlConfig raises ImportError'):
            with t.assertRaises(ImportError) as err:
                _ = _load_yaml_file(file_path=t.file_path)
                t.assertEqual(err.msg, "wark")
