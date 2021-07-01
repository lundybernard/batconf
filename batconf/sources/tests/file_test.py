from unittest import TestCase
from unittest.mock import patch, mock_open, create_autospec


from ..file import (
    FileConfig,
    load_config_file,
    yaml,
    os,
    Path,
    _missing_config_warning,
)


SRC = 'batconf.sources.file'


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

EXAMPLE_CONFIG_DICT = yaml.load(EXAMPLE_CONFIG_YAML, Loader=yaml.BaseLoader)


class TestFileConfig(TestCase):

    def setUp(t):
        patches = ['Path', ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t.Path.is_file.return_value = True
        t.m_open = mock_open(read_data=EXAMPLE_CONFIG_YAML)

    def test_get(t):
        with patch('builtins.open', t.m_open):
            conf = FileConfig()

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

    def test_default_file(t):
        DEFAULT_FILE = '/config.yaml'

        with patch('builtins.open', t.m_open):
            FileConfig()

        t.m_open.assert_called_with(
            t.Path(os.getcwd() + DEFAULT_FILE)
        )

    def test_loads_given_config_file(t):
        with patch('builtins.open', t.m_open):
            FileConfig(
                './test_example.config.yaml', config_env='example'
            )
        t.m_open.assert_called_with('./test_example.config.yaml')

    def test_config_env_argument(t):
        with patch('builtins.open', t.m_open):
            config_file = FileConfig(
                './example.config.yaml', config_env='alt'
            )
        t.m_open.assert_called_with('./example.config.yaml')
        t.assertEqual(
            config_file.get('key', module='bat.module'), 'alt_value'
        )

    def test__getitem__(t):
        with patch('builtins.open', t.m_open):
            config_file = FileConfig()

        with t.subTest('dot notation key path'):
            t.assertEqual(
                config_file['bat.remote_host.api_key'],
                'example_api_key'
            )
        with t.subTest('__getitem__ chain'):
            t.assertEqual(
                config_file['bat']['remote_host']['url'],
                'https://api-example.host.io/'
            )

    def test_keys(t):
        with patch('builtins.open', t.m_open):
            config_file = FileConfig()

        t.assertEqual(config_file.keys(), {'bat': None}.keys())


class Test_load_config_file(TestCase):

    def setUp(t):
        t.m_open = mock_open(read_data=EXAMPLE_CONFIG_YAML)

    def test_arg_config_file_name(t):
        with patch('builtins.open', t.m_open):
            conf = load_config_file('./example.config.yaml')

        t.m_open.assert_called_with('./example.config.yaml')
        t.assertEqual(conf, EXAMPLE_CONFIG_DICT)

    def test_config_default_config_env(t):
        with patch('builtins.open', t.m_open):
            conf = load_config_file('./example.config.yaml')

        t.assertEqual(conf['default'], 'example')

        default_env = conf[conf['default']]

        t.assertEqual(default_env, conf['example'])

    @patch.dict(
        f'{SRC}.os.environ', {'BAT_CONFIG_FILE': 'env.config.yaml'}
    )
    def test_config_file_env_variable(t):
        with patch('builtins.open', t.m_open):
            conf = load_config_file()

        t.m_open.assert_called_with('env.config.yaml')

        example_env = conf['example']['bat']
        t.assertEqual(
            example_env['remote_host']['api_key'],
            'example_api_key'
        )
        t.assertEqual(
            example_env['remote_host']['url'],
            'https://api-example.host.io/'
        )

    @patch.dict(f'{SRC}.os.environ', {}, clear=True)
    def test_default_config_file(t):
        Path.is_file = create_autospec(
            Path.is_file, spec_set=True, return_value=True
        )
        t.m_open = mock_open(read_data=EXAMPLE_CONFIG_YAML)

        with patch('builtins.open', t.m_open):
            CONF = load_config_file()

        t.m_open.assert_called_with(
            Path(os.getcwd() + '/config.yaml')
        )
        example_env = CONF['example']['bat']
        t.assertEqual(
            example_env['remote_host']['api_key'],
            'example_api_key'
        )
        t.assertEqual(
            example_env['remote_host']['url'],
            'https://api-example.host.io/'
        )

    @patch.dict(f'{SRC}.os.environ', {}, clear=True)
    @patch(f'{SRC}.log', autospec=True)
    @patch(f'{SRC}.Path.is_file', autospec=True)
    def test_config_missing_file(t, path_is_file, log):
        '''PROJECT_CONFIG is not set
        '''
        path_is_file.return_value = False
        conf = load_config_file()
        log.warn.assert_called_with(_missing_config_warning)
        t.assertEqual(conf['default'], 'none')
