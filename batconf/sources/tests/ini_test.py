from unittest import TestCase
from unittest.mock import Mock, patch

from ..ini import (
    # Under Test
    IniConfig,
    IniConfigEnvs,
    IniConfigSect,
    IniConfigFlat,
    _load_ini_file,
    _load_ini,
    # Helpers
    ConfigParser,
    Path,
)


SRC = 'batconf.sources.ini'


# Sample .ini data as a string
INI_STR = """
[batconf]
default_env = development

[development]
environment = development

[development.project]
user = Dummy Plug

[development.project.database]
host = localhost/mydb
token = *token-str*

# Include configs for 3rd party libraries
[development.pandas]
[development.pandas.diplay]
max_rows = 1000
max_columns = 1000

[production]
[production.project]
user = Morgan B.

[production.branch "wired"]
user = knights
"""

EXAMPLE_CONFIGPARSER = ConfigParser()
EXAMPLE_CONFIGPARSER.read_string(INI_STR)


EXAMPLE_FLAT_STR = """
[your-project-name]
k1 = v1
key with spaces: val with spaces
key.with.dots = val.with.dots
"""

EXAMPLE_FLAT_CONFIGPARSER = ConfigParser()
EXAMPLE_FLAT_CONFIGPARSER.read_string(EXAMPLE_FLAT_STR)


# Maybe removed, we are not getting an acutal dict from ConfigParser
EXAMPLE_CONFIG_DICT: dict = {
    'batconf': {'default_env': 'development'},
    'development': {
        'environment': 'development',
        'project': {
            'user': 'Dummy Plug',
            'database': {
                'host': 'localhost/mydb',
                'token': '*token-str*'
            }
        }
    },
    'production': {
        'project': {'user': 'Morgan B.'}
    }
}

INI_CONIG_PARSER = ConfigParser()
INI_CONIG_PARSER.read_string(INI_STR)


class IniConfigFactoryTests(TestCase):
    @patch(f'{SRC}.IniConfigEnvs', autospec=True)
    def test_defaults(t, IniConfigEnvs: Mock):
        config = IniConfig('testconfig.ini')
        t.assertIs(IniConfigEnvs.return_value, config)
        IniConfigEnvs.assert_called_with(
            file_path='testconfig.ini',
            config_env=None,
            missing_file_option='warn',
        )

    @patch(f'{SRC}.IniConfigEnvs', autospec=True)
    def test_environments_format(t, IniConfigEnvs: Mock):
        config = IniConfig(
            file_path='testconfig.ini',
            config_env='production',
            missing_file_option='ignore',
            file_format='environments',
        )
        t.assertIs(IniConfigEnvs.return_value, config)
        IniConfigEnvs.assert_called_with(
            file_path='testconfig.ini',
            config_env='production',
            missing_file_option='ignore',
        )

    @patch(f'{SRC}.IniConfigEnvs', autospec=True)
    def test_config_env_argument(t, IniConfigEnvs: Mock):
        '''The config_env parameter is passed to the IniConfigEnvs
        when it is specified.
        '''
        config = IniConfig(
            file_path='testconfig.ini',
            config_env='production',
        )
        t.assertIs(IniConfigEnvs.return_value, config)
        IniConfigEnvs.assert_called_with(
            file_path='testconfig.ini',
            config_env='production',
            missing_file_option='warn',
        )

    @patch(f'{SRC}.IniConfigSect', autospec=True)
    def test_sections_format(t, IniConfigSect: Mock):
        config = IniConfig(
            file_path='testconfig.ini',
            missing_file_option='ignore',
            file_format='sections',
        )
        t.assertIs(IniConfigSect.return_value, config)
        IniConfigSect.assert_called_with(
            file_path='testconfig.ini',
            missing_file_option='ignore',
        )

    @patch(f'{SRC}.IniConfigFlat', autospec=True)
    def test_flat_format(t, IniConfigFlat: Mock):
        config = IniConfig(
            file_path='testconfig.ini',
            missing_file_option='ignore',
            file_format='flat',
        )
        t.assertIs(IniConfigFlat.return_value, config)
        IniConfigFlat.assert_called_with(
            file_path='testconfig.ini',
            missing_file_option='ignore',
        )


class IniConfigEnvsTests(TestCase):
    _load_ini_file: Mock

    def setUp(t):
        patches = ['_load_ini_file', ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t._load_ini_file.return_value = INI_CONIG_PARSER

    def test_get(t):
        conf = IniConfigEnvs('testconfig.ini')

        t.assertEqual(conf.get('project.user'), 'Dummy Plug')
        t.assertEqual(conf.get('project.database.host'), 'localhost/mydb')
        t.assertEqual(conf.get('project.database.token'), '*token-str*')

        with t.subTest('single key'):
            t.assertEqual(
                conf.get('environment'),
                EXAMPLE_CONFIGPARSER.get('development','environment')
            )

        with t.subTest('missing item'):
            t.assertEqual(conf.get('_sir_not_appearing_in_this_film'), None)
            t.assertEqual(conf.get('sir.not.appearing.in.this.film'), None)

    def test_get_raises_err_for_module_parameter(t):
        # TODO: remove this check when the SourceInterface.get
        #  module parameter is removed.
        t.conf = IniConfigEnvs('testconfig.ini')
        with t.assertRaises(NotImplementedError) as err:
            t.conf.get('project.user', module='this.throws.an.error')

        t.assertEqual(
            str(err.exception),
            'The module argument is deprecated and will be removed'
            ' from the SourceInterface.get interface in a future release.',
        )

    def test__default_env(t):
        '''Default environment is extracted from the config file
        else it is None
        '''
        conf = IniConfigEnvs('testconfig.ini')
        t.assertEqual(
            conf._config_env,
            EXAMPLE_CONFIGPARSER.get('batconf','default_env'),
        )
        t.assertEqual(conf.get('project.user'), 'Dummy Plug')

    def test_config_env(t):
        '''Given a config_env, the config values will be loaded from
        the specified section of the .ini file.
        '''

        conf = IniConfigEnvs('testconfig.ini', config_env='production')
        t.assertEqual(conf._config_env, 'production')
        t.assertEqual(
            conf.get('project.user'),
            EXAMPLE_CONFIGPARSER.get('production.project', 'user')
        )

    def test__config_env_invalid_section_raises_err(t):
        with t.assertRaises(ValueError) as err:
            _ = IniConfigEnvs(
                file_path='testconfig.ini',
                config_env='sir.not.appearing.in.this.film',
            )

        t.assertEqual(
            str(err.exception),
            'Config Environment "sir.not.appearing.in.this.film"'
            ' not found in testconfig.ini',
        )


class IniFileLoaderTests(TestCase):
    def setUp(t):
        t.file_path = Path('testconfig.ini')

    def test_EXAMPLE_CONFIGPARSER(t):
        # the loaded ConfigParser contains the full contence of the .ini file
        t.assertEqual(
            'development',
            EXAMPLE_CONFIGPARSER.get('batconf', 'default_env')
        )
        t.assertEqual(
            'Dummy Plug',
            EXAMPLE_CONFIGPARSER.get('development.project', 'user')
        )
        t.assertEqual(
            '*token-str*',
            EXAMPLE_CONFIGPARSER.get('development.project.database', 'token'),
        )
        t.assertEqual(
            'Morgan B.',
            EXAMPLE_CONFIGPARSER.get('production.project', 'user')
        )

    @patch(f'{SRC}.ConfigParser', autospec=True)
    def test__load_ini_file(t, ConfigParser: Mock):
        config_parser_instance = ConfigParser.return_value

        with t.subTest('file found'):
            config_parser = _load_ini_file(file_path=t.file_path)

            t.assertIs(config_parser_instance, config_parser)
            config_parser_instance.read.assert_called_with(t.file_path)

        with t.subTest('missing file'):
            # when a file is not found, config_parser returns and empty list
            config_parser_instance.read.return_value = []
            with t.assertRaises(FileNotFoundError):
                _ = _load_ini_file(file_path=t.file_path)

    @patch(f'{SRC}.load_file_warn_when_mising', autospec=True)
    def test__load_ini_warn(t, load_file_warn_when_mising: Mock):
        ret = _load_ini(file_path=t.file_path, when_missing='warn')
        load_file_warn_when_mising.assert_called_with(
            file_path=t.file_path,
            loader_fn=_load_ini_file,
        )
        t.assertIs(load_file_warn_when_mising.return_value, ret)

    @patch(f'{SRC}.load_file_ignore_when_missing', autospec=True)
    def test__load_ini_ignore(t, load_file_ignore_when_missing: Mock):
        ret = _load_ini(file_path=t.file_path, when_missing='ignore')
        load_file_ignore_when_missing.assert_called_with(
            file_path=t.file_path,
            loader_fn=_load_ini_file,
        )
        t.assertIs(load_file_ignore_when_missing.return_value, ret)

    @patch(f'{SRC}._load_ini_file', autospec=True)
    def test__load_ini_error(t, _load_ini_file: Mock):
        _load_ini_file.side_effect = FileNotFoundError
        with t.assertRaises(FileNotFoundError) as err:
            _ = _load_ini(file_path=t.file_path, when_missing='error')

        _load_ini_file.assert_called_with(file_path=t.file_path)

    def test__load_ini(t):
        with (t.subTest('default: when_missing="warn"')):
            with patch(
                f'{SRC}.load_file_warn_when_mising',
                autospec=True,
            ) as load_file_warn_when_mising:
                _ = _load_ini(file_path=t.file_path)
                load_file_warn_when_mising.assert_called_with(
                    loader_fn=_load_ini_file,
                    file_path=Path('testconfig.ini')
                )
                
        with t.subTest('when_missing="ignore"'):
            with patch(
                f'{SRC}.load_file_ignore_when_missing',
                    autospec=True,
            ) as load_file_ignore_when_missing:
                _ = _load_ini(
                    file_path=t.file_path,
                    when_missing='ignore',
                )
                load_file_ignore_when_missing.assert_called_with(
                    loader_fn=_load_ini_file,
                    file_path=Path('testconfig.ini')
                )
                
        with t.subTest('when_missing="error"'):
            with patch(
                f'{SRC}._load_ini_file',
                autospec=True,
            ) as load_ini_file:
                load_ini_file.side_effect = FileNotFoundError
                with t.assertRaises(FileNotFoundError):
                    _ = _load_ini(
                        file_path=t.file_path,
                        when_missing='error',
                    )
