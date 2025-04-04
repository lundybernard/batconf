from unittest import TestCase
from unittest.mock import Mock, patch, mock_open

from ..ini import (
    # Under Test
    IniConfig,
    ConfigFileFormats,
    _load_ini_file,
    _load_ini_file_flat,
    _load_ini,
    _getter_methods,
    _get_envs,
    _get_sections,
    _get_flat,
    _get_empty,
    _file_type_loaders,
    _missing_file_handlers,
    ConfigParser,
    EmptyConfigParser,
    Path,
    load_file_warn_when_missing,
    load_file_ignore_when_missing,
    load_file_error_when_missing,
)


SRC = 'batconf.sources.ini'


# Sample .ini data as a string
INI_ENV_STR = """
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
environment = production
[production.project]
user = Morgan B.

[production.branch "wired"]
user = knights
"""


EXAMPLE_SECTIONS_STR = """
[sec0]
k0 = s0v0
[sec1]
k0 = s1v0
"""


EXAMPLE_FLAT_STR = """
k1 = v1
key with spaces: val with spaces
key.with.dots = val.with.dots
"""


# Maybe removed, we are not getting an acutal dict from ConfigParser
EXAMPLE_CONFIG_DICT: dict = {
    'batconf': {'default_env': 'development'},
    'development': {
        'environment': 'development',
        'project': {
            'user': 'Dummy Plug',
            'database': {'host': 'localhost/mydb', 'token': '*token-str*'},
        },
    },
    'production': {'project': {'user': 'Morgan B.'}},
}


CONFIG_PARSER_ENVS = ConfigParser()
CONFIG_PARSER_ENVS.read_string(INI_ENV_STR)


class IniConfigTests(TestCase):
    _load_ini: Mock

    def setUp(t):
        patches = [
            '_load_ini',
        ]
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        t._load_ini.return_value = CONFIG_PARSER_ENVS

        t.config_file_str = 'testconfig.ini'

    def test___init__defaults(t):
        ic = IniConfig(
            file_path=t.config_file_str,
            # Default: config_env=* loads default from file
            # Default: file_format='environments',
            # Default: missing_file_option='warn',
        )

        t.assertEqual(ic._file_format, 'environments')
        t.assertEqual(ic._missing_file_option, 'warn')
        t.assertEqual(ic._config_file_path, Path(t.config_file_str))

        t.assertIs(ic._data, t._load_ini.return_value)
        config_env = CONFIG_PARSER_ENVS.get('batconf', 'default_env')
        t.assertEqual(config_env, 'development')
        t.assertEqual(ic._config_env, config_env)
        t.assertIs(ic._get_impl, _getter_methods['environments'])

    def test___init__catches_invalid_file_format(t):
        with t.assertRaises(ValueError):
            _ = IniConfig(file_path=t.config_file_str, file_format='invalid')

    def test_get(t):
        """The get method calls the expected _get_config variant"""
        ic = IniConfig(file_path=t.config_file_str)
        _get_config_mock = Mock(_get_envs, autospec=True)

        ic._get_impl = _get_config_mock

        ret = ic.get(key='section.key')

        _get_config_mock.assert_called_with(ic, key='section.key', path=None)
        t.assertIs(ret, _get_config_mock.return_value)

        with t.subTest('path parameter'):
            ret = ic.get(key='key', path='section.sub')
            _get_config_mock.assert_called_with(
                ic,
                key='key',
                path='section.sub',
            )
            t.assertIs(ret, _get_config_mock.return_value)

    def test_get_legacy_path_parameter(t):
        """The path parameter is expected to be deprecated in the near future,
        but we still need it to respect how the Configuration class
        currently handles path lookups.
        """
        ic = IniConfig(file_path=t.config_file_str)
        ret = ic.get(key='token', path='project.database')
        t.assertEqual('*token-str*', ret)

    # === .ini file format options === #
    def test_file_format_sections(t):
        ic = IniConfig(
            file_path=t.config_file_str,
            file_format='sections',
            # Default: missing_file_option='warn',
        )

        t.assertEqual(ic._file_format, 'sections')
        # _config_env is not set for 'sections' file format
        t.assertEqual(ic._config_env, None)
        t.assertIs(ic._get_impl, _getter_methods['sections'])

    def test_environments_format(t):
        file_format = 'environments'
        config_env = 'production'

        ic = IniConfig(
            file_path=t.config_file_str,
            config_env=config_env,
            file_format=file_format,
        )

        t.assertEqual(ic._file_format, file_format)
        t.assertEqual(ic._config_env, config_env)
        t.assertIs(ic._get_impl, _getter_methods[file_format])

    def test_flat_format(t):
        file_format = 'flat'

        ic = IniConfig(
            file_path=t.config_file_str,
            file_format=file_format,
        )

        t.assertEqual(ic._file_format, file_format)
        # _config_env is not set for 'flat' file format
        t.assertIsNone(ic._config_env)
        t.assertIs(ic._get_impl, _getter_methods[file_format])

    # === Missing File Handling === #

    def test_missing_file_options(t):
        """
        The IniConfig class does not handle missing files directly.
        'warn' is passed to the _load_ini function,
        which handles emitting the warning message
        _data cannot be loaded, so it is replaced with an EmptyConfigParser
        _config_env cannot be set from the config file, so it is set to None
        """
        t._load_ini.return_value = EmptyConfigParser

        for option in ('warn', 'ignore', 'error'):
            with t.subTest(f'missing_file_option={option}'):
                ic = IniConfig(
                    file_path=t.config_file_str,
                    missing_file_option=option,
                )

                t._load_ini.assert_called_with(
                    file_path=Path(t.config_file_str),
                    file_format='environments',
                    when_missing=option,
                )
                t.assertIs(ic._data, EmptyConfigParser)
                t.assertIsNone(ic._config_env)

    def test_config_env_argument(t):
        """Validate and set the config_env parameter
        Code Smell: there's a log of complexity here, may need refactoring
        """
        config_env = 'production'

        with t.subTest('default environments file format'):
            """If the config_env is not specified,
            extract it from the configuration file
            """
            ic = IniConfig(
                file_path=t.config_file_str,
                file_format='environments',
            )
            t.assertEqual(
                ic._config_env,
                CONFIG_PARSER_ENVS.get('batconf', 'default_env'),
            )

        with t.subTest('environments file format'):
            """Given a config_env, when the file format is 'environments',
            save the given environment
            """
            ic = IniConfig(
                file_path=t.config_file_str,
                config_env=config_env,
            )
            t.assertEqual(ic._config_env, config_env)

        with t.subTest('config_env section missing from file'):
            """raise a Value Error 
            when the specified section is not in the config file
            """
            with t.assertRaises(ValueError) as err:
                _ = IniConfig(
                    file_path=t.config_file_str,
                    config_env='MissingEnvironment',
                )
            t.assertEqual(
                str(err.exception),
                'Config Environment "MissingEnvironment" not found in testconfig.ini',
            )

        with t.subTest('missing environments format file'):
            """When the ini file is not found
            set _config_env to None
            """
            t._load_ini.return_value = EmptyConfigParser
            ic = IniConfig(
                file_path=t.config_file_str,
                config_env=config_env,
                file_format='environments',
            )
            t.assertIsNone(ic._config_env)

        # flat and sections formats set _config_env to None
        for file_format, config_parser in (
            (ff, p)
            for ff in ('flat', 'sections')
            for p in (ConfigParser, EmptyConfigParser)
        ):
            with t.subTest(
                f'_config_env is None when {file_format=} and {config_parser=}'
            ):
                t._load_ini.return_value = config_parser
                ic = IniConfig(
                    file_path=t.config_file_str,
                    file_format=file_format,
                )
                t.assertIsNone(ic._config_env)

    def test_get_methods_for_file_formats(t) -> None:
        formats: list[ConfigFileFormats] = [
            'flat',
            'sections',
            'environments',
        ]
        for fmt in formats:
            with t.subTest(f'get_impl for {fmt}'):
                ic = IniConfig(
                    file_path=t.config_file_str,
                    file_format=fmt,
                )
                t.assertIs(ic._get_impl, _getter_methods[fmt])


class GetConfigFunctionsTests(TestCase):
    def setUp(t):
        t.ic = Mock(IniConfig, autospec=True)
        t.ic._config_env = 'testing'
        t.key = 'key'

    def test__get_envs(t):
        """Gets values from a ConfigParser
        which uses batconf-style environment sections
        """
        with t.subTest('single key'):
            """Getting a single-key, 
            looks for the key in the _config_env section
            """
            ret = _get_envs(self=t.ic, key=t.key)
            t.ic._data.get.assert_called_with(
                option=t.key,
                section=f'{t.ic._config_env}',
                fallback=None,
            )
            t.assertIs(ret, t.ic._data.get.return_value)

        with t.subTest('path.to.key string'):
            """given a '.' delimited fully* qualified key,
            split off the rt.most value for the key,
            and prepend the _config_environment to the section
            """
            ret = _get_envs(self=t.ic, key='section.sub.key')
            t.ic._data.get.assert_called_with(
                option=t.key,
                section=f'{t.ic._config_env}.section.sub',
                fallback=None,
            )
            t.assertIs(ret, t.ic._data.get.return_value)

        with t.subTest('legacy path parameter'):
            ret = _get_envs(self=t.ic, key='key', path='section.sub')
            t.ic._data.get.assert_called_with(
                option=t.key,
                section=f'{t.ic._config_env}.section.sub',
                fallback=None,
            )
            t.assertIs(ret, t.ic._data.get.return_value)

    def test__get_sections(t) -> None:
        """Get values from a ConfigParser which has sections
        but does not use batconf-style environment sections.
        This is for the standard .ini file format.
        """
        with t.subTest('single key'):
            # Section files require a section be specified
            ret = _get_sections(self=t.ic, key=t.key)
            t.ic._data.get.assert_called_with(
                option=t.key,
                section='',  # this should fail and fallback to None
                fallback=None,
            )
            # but returning None is handled by the _data.get method
            t.assertIs(ret, t.ic._data.get.return_value)

        with t.subTest('section.key'):
            ret = _get_sections(self=t.ic, key='section.key')
            t.ic._data.get.assert_called_with(
                option='key',
                section='section',
                fallback=None,
            )
            t.assertIs(ret, t.ic._data.get.return_value)

        with t.subTest('legacy path parameter'):
            ret = _get_sections(self=t.ic, key='key', path='section.sub')
            t.ic._data.get.assert_called_with(
                option=t.key,
                section='section.sub',
                fallback=None,
            )
            t.assertIs(ret, t.ic._data.get.return_value)

    def test__get_flat(t):
        """Flat files contain no sections
        * a default 'root' section is injected into the ConfigParser
        So only single-key lookups are valid...
        however keys can be delimited with '.'

        This is valid flat formatted config.ini contents:
            section.key=value
            section.key2=value2
            section.subsection.key=value3
        """
        with t.subTest('single key'):
            ret = _get_flat(self=t.ic, key=t.key)
            t.ic._data.get.assert_called_with(
                option=t.key,
                section='root',
                fallback=None,
            )
            t.assertIs(ret, t.ic._data.get.return_value)

        with t.subTest('dot.delimited.key'):
            ret = _get_flat(self=t.ic, key='this.is.a.valid.key')
            t.ic._data.get.assert_called_with(
                # the key is not split, it is taken literally
                option='this.is.a.valid.key',
                section='root',  # Uses the injected root section value
                fallback=None,
            )
            t.assertIs(ret, t.ic._data.get.return_value)

    def test__get_empty(t) -> None:
        """_get_empty always returns None"""
        ret = _get_empty(self=t.ic, key=t.key)
        # All values are None
        t.assertIsNone(ret)
        t.assertIsNone(_get_empty(self=t.ic, key='any.key'))


class _load_ini_file_Tests(TestCase):
    def setUp(t):
        t.file_str = 'testconfig.ini'
        t.file_path = Path(t.file_str)

    @patch(f'{SRC}.ConfigParser', autospec=True)
    def test__load_ini_file(t, ConfigParser: Mock):
        config_parser_instance = ConfigParser.return_value

        ret = _load_ini_file(file_path=t.file_path)

        t.assertIs(config_parser_instance, ret)
        config_parser_instance.read.assert_called_with(t.file_path)

    @patch(f'{SRC}.ConfigParser', autospec=True)
    def test_load_ini_file_missing_file(t, ConfigParser: Mock):
        # when a file is not found, config_parser returns and empty list
        config_parser_instance = ConfigParser.return_value
        config_parser_instance.read.return_value = []

        with t.assertRaises(FileNotFoundError):
            _ = _load_ini_file(file_path=t.file_path)


class _load_ini_file_flat_Tests(TestCase):
    ConfigParser: Mock

    def setUp(t):
        patches = ['ConfigParser']
        for target in patches:
            patcher = patch(f'{SRC}.{target}', autospec=True)
            setattr(t, target, patcher.start())
            t.addCleanup(patcher.stop)

        # Patch out the `with open` statement, so it returns the mock_open obj
        t.m_open = mock_open(read_data=EXAMPLE_FLAT_STR)
        open_patcher = patch('builtins.open', t.m_open)
        t.open = open_patcher.start()
        t.addCleanup(open_patcher.stop)

        t.file_str = 'testconfig.ini'
        t.file_path = Path(t.file_str)
        t.config_parser = t.ConfigParser.return_value

    def test__load_ini_file(t):
        ret = _load_ini_file_flat(file_path=t.file_path)

        t.assertIs(t.config_parser, ret)
        t.config_parser.read_string.assert_called_with(
            f'[root]\n{EXAMPLE_FLAT_STR}'
        )

    def test_file_not_found(t):
        t.m_open.side_effect = FileNotFoundError

        with t.assertRaises(FileNotFoundError):
            _ = _load_ini_file_flat(file_path=t.file_path)


class _load_ini_Tests(TestCase):
    """Tests for the _load_ini function"""

    mock_missing_file_handlers = {
        'warn': Mock(load_file_warn_when_missing, autospec=True),
        'ignore': Mock(load_file_ignore_when_missing, autospec=True),
        'error': Mock(load_file_error_when_missing, autospec=True),
    }

    @patch.dict(f'{SRC}._missing_file_handlers', mock_missing_file_handlers)
    def test__load_ini(t):
        t.file_str = 'testconfig.ini'
        t.file_path = Path(t.file_str)

        for file_format in ('sections', 'environments', 'flat'):
            for when_missing in ('warn', 'ignore', 'error'):
                with t.subTest(f'{file_format=} {when_missing=}'):
                    ret = _load_ini(
                        file_path=t.file_path,
                        file_format=file_format,
                        when_missing=when_missing,
                    )
                    _missing_file_handlers[when_missing].assert_called_with(
                        file_path=t.file_path,
                        loader_fn=_file_type_loaders[file_format],
                        empty_fallback=EmptyConfigParser,
                    )
                    t.assertIs(
                        ret, _missing_file_handlers[when_missing].return_value
                    )


class GlobalsTests(TestCase):
    """test global variables in this test file"""

    def test_CONFIG_PARSER_ENVS(t):
        """Test some assumptions we rely on about how ConfigParser functions"""
        t.assertEqual(
            [
                'batconf',
                'development',
                'development.project',
                'development.project.database',
                'development.pandas',
                'development.pandas.diplay',
                'production',
                'production.project',
                'production.branch "wired"',
            ],
            CONFIG_PARSER_ENVS.sections(),
        )

    def test_get_batconf_default_env(t):
        # the loaded ConfigParser contains the full contence of the .ini file
        t.assertEqual(
            'development', CONFIG_PARSER_ENVS.get('batconf', 'default_env')
        )

    def test_get_value_from_dev_environment(t):
        t.assertEqual(
            'Dummy Plug',
            CONFIG_PARSER_ENVS.get('development.project', 'user'),
        )

    def test_get_value_from_dev_environment_subsection(t):
        t.assertEqual(
            '*token-str*',
            CONFIG_PARSER_ENVS.get('development.project.database', 'token'),
        )

    def test_get_value_from_prod_environment(t):
        t.assertEqual(
            'Morgan B.',
            CONFIG_PARSER_ENVS.get('production.project', 'user'),
        )

    # === __getitem__ notes === #
    def test_CONFIG_PARSER_ENVS_contains_all_environments(t):
        t.assertEqual(
            CONFIG_PARSER_ENVS['batconf']['default_env'],
            'development',
        )
        t.assertEqual(
            CONFIG_PARSER_ENVS['production']['environment'],
            'production',
        )

    def test_ConfigParser_is_not_nested(t):
        # Chaining getitem calls fails
        with t.assertRaises(KeyError):
            _ = CONFIG_PARSER_ENVS['production']['project']

        # First getitem for the section (path),
        # then get the key value
        t.assertEqual(
            CONFIG_PARSER_ENVS['production.project']['user'],
            'Morgan B.',
        )
        # We cannot short-cut by using {section}.{key}
        with t.assertRaises(KeyError):
            t.assertEqual(
                CONFIG_PARSER_ENVS['production.project.user'],
                'Morgan B.',
            )
