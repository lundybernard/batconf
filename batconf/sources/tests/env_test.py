from unittest import TestCase
from unittest.mock import Mock, patch

from ..env import _BAT_PREFIX_DEPRECATION, EnvSource


SRC = 'batconf.sources.env'


class TestEnvSource(TestCase):
    def setUp(t) -> None:
        t.es = EnvSource(prefix='mytool')

    @patch.dict(
        f'{SRC}.os.environ',
        {
            'MYTOOL_CONFIG_FILE': 'example.config.yaml',
            'MYTOOL_MODULE_KEY': 'value',
            'MYTOOL_MODULE_PATH_TO_KEY': 'value2',
        },
    )
    def test_get(t):
        with t.subTest('single key'):
            t.assertEqual(t.es.get('config_file'), 'example.config.yaml')

        with t.subTest('missing value'):
            t.assertEqual(t.es.get('remote_host'), None)

        with t.subTest('path value'):
            t.assertEqual(t.es.get('key', path='module'), 'value')

        with t.subTest('path and key paths'):
            t.assertEqual(t.es.get('to.key', path='module.path'), 'value2')

    def test_env_name(t):
        with t.subTest('the prefix leads a bare key'):
            t.assertEqual(t.es.env_name('key'), 'MYTOOL_KEY')

        with t.subTest('the prefix leads a dotted key'):
            t.assertEqual(t.es.env_name('path.to.key'), 'MYTOOL_PATH_TO_KEY')

        with t.subTest('the prefix leads the config path'):
            t.assertEqual(
                t.es.env_name('key', path='module'), 'MYTOOL_MODULE_KEY'
            )

        with t.subTest('path and key paths'):
            t.assertEqual(
                t.es.env_name('to.key', path='module.path'),
                'MYTOOL_MODULE_PATH_TO_KEY',
            )

        with t.subTest('prefix=None declares no namespace'):
            source = EnvSource(prefix=None)
            t.assertEqual(
                source.env_name('key', path='server'), 'SERVER_KEY'
            )
            t.assertEqual(source.env_name('key'), 'KEY')

    def test___str__(t) -> None:
        t.assertEqual(f'Environment Variables: {repr(t.es)}', str(t.es))

    def test___repr__(t) -> None:
        t.assertEqual('EnvSource()', repr(t.es))


class BatPrefixDeprecationTests(TestCase):
    """An undeclared prefix keeps the BAT prefix, and warns."""

    warnings: Mock

    def setUp(t) -> None:
        patcher = patch(f'{SRC}.warnings', autospec=True)
        t.warnings = patcher.start()
        t.addCleanup(patcher.stop)
        t.es = EnvSource()  # prefix undeclared: pre-0.5.0 behaviour

    def test_env_name(t):
        with t.subTest('an empty path keeps the BAT prefix, and warns'):
            t.assertEqual('BAT_KEY', t.es.env_name('key'))
            t.warnings.warn.assert_called_once_with(
                _BAT_PREFIX_DEPRECATION,
                DeprecationWarning,
                stacklevel=4,
            )

        with t.subTest('a declared path resolves unprefixed, no warning'):
            t.warnings.reset_mock()
            t.assertEqual(
                'SERVER_HOST', t.es.env_name('host', path='server')
            )
            t.warnings.warn.assert_not_called()

    def test__BAT_PREFIX_DEPRECATION(t):
        t.assertEqual(
            "the implicit 'BAT' environment prefix is deprecated and will "
            'be removed in v0.5.0; pass prefix=None for no prefix, or a '
            'namespace of your own.',
            _BAT_PREFIX_DEPRECATION,
        )


class EnvNameModuleDeprecationTests(TestCase):
    """env_name routes its deprecated module keyword through the shim."""

    deprecated_module: Mock

    def setUp(t) -> None:
        patcher = patch(f'{SRC}.deprecated_module', autospec=True)
        t.deprecated_module = patcher.start()
        t.addCleanup(patcher.stop)
        t.es = EnvSource(prefix='mytool')

    def test_env_name(t):
        t.deprecated_module.return_value = 'server'

        t.assertEqual('MYTOOL_SERVER_KEY', t.es.env_name('key', module='m'))
        t.deprecated_module.assert_called_once_with(
            None, 'm', method='env_name'
        )
