from unittest import TestCase
from unittest.mock import Mock, patch

from ..env import _BAT_PREFIX_DEPRECATION, _UNSET, EnvSource


SRC = 'batconf.sources.env'


class EnvSourceTests(TestCase):
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
    def test_get(t) -> None:
        with t.subTest('single key'):
            ret = t.es.get('config_file')
            t.assertEqual('example.config.yaml', ret)

        with t.subTest('missing value'):
            ret = t.es.get('remote_host')
            t.assertEqual(None, ret)

        with t.subTest('path value'):
            ret = t.es.get('key', path='module')
            t.assertEqual('value', ret)

        with t.subTest('path and key paths'):
            ret = t.es.get('to.key', path='module.path')
            t.assertEqual('value2', ret)

    def test_env_name(t) -> None:
        with t.subTest('the prefix leads a bare key'):
            ret = t.es.env_name('key')
            t.assertEqual('MYTOOL_KEY', ret)

        with t.subTest('the prefix leads a dotted key'):
            ret = t.es.env_name('path.to.key')
            t.assertEqual('MYTOOL_PATH_TO_KEY', ret)

        with t.subTest('the prefix leads the config path'):
            ret = t.es.env_name('key', path='module')
            t.assertEqual('MYTOOL_MODULE_KEY', ret)

        with t.subTest('path and key paths'):
            ret = t.es.env_name('to.key', path='module.path')
            t.assertEqual('MYTOOL_MODULE_PATH_TO_KEY', ret)

        with t.subTest('prefix=None declares no namespace under a path'):
            t.es._prefix = None
            ret = t.es.env_name('key', path='server')
            t.assertEqual('SERVER_KEY', ret)

        with t.subTest('prefix=None declares no namespace at the root'):
            t.es._prefix = None
            ret = t.es.env_name('key')
            t.assertEqual('KEY', ret)

    def test___str__(t) -> None:
        ret = str(t.es)
        t.assertEqual(f'Environment Variables: {repr(t.es)}', ret)

    def test___repr__(t) -> None:
        with t.subTest('an undeclared prefix prints no argument'):
            t.es._prefix = _UNSET
            ret = repr(t.es)
            t.assertEqual('EnvSource()', ret)

        with t.subTest('a declared prefix prints quoted'):
            t.es._prefix = 'mytool'
            ret = repr(t.es)
            t.assertEqual("EnvSource(prefix='mytool')", ret)

        with t.subTest('prefix=None prints None'):
            t.es._prefix = None
            ret = repr(t.es)
            t.assertEqual('EnvSource(prefix=None)', ret)


class BatPrefixDeprecationTests(TestCase):
    """An undeclared prefix keeps the BAT prefix, and warns."""

    warnings: Mock

    def setUp(t) -> None:
        patcher = patch(f'{SRC}.warnings', autospec=True)
        t.warnings = patcher.start()
        t.addCleanup(patcher.stop)
        t.es = EnvSource()  # prefix undeclared: pre-0.5.0 behaviour

    def test_env_name(t) -> None:
        with t.subTest('an empty path keeps the BAT prefix, and warns'):
            ret = t.es.env_name('key')

            t.assertEqual('BAT_KEY', ret)
            t.warnings.warn.assert_called_once_with(
                _BAT_PREFIX_DEPRECATION,
                DeprecationWarning,
                stacklevel=4,
            )

        with t.subTest('a declared path resolves unprefixed, no warning'):
            t.warnings.reset_mock()

            ret = t.es.env_name('host', path='server')

            t.assertEqual('SERVER_HOST', ret)
            t.warnings.warn.assert_not_called()

    def test__BAT_PREFIX_DEPRECATION(t) -> None:
        t.assertEqual(
            "the implicit 'BAT' environment prefix is deprecated and will "
            "be removed in v0.5.0; pass prefix='BAT' to keep it, or "
            'prefix=None for no prefix.',
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

    def test_env_name(t) -> None:
        t.deprecated_module.return_value = 'server'

        ret = t.es.env_name('key', module='m')

        t.assertEqual('MYTOOL_SERVER_KEY', ret)
        t.deprecated_module.assert_called_once_with(
            None, 'm', method='env_name'
        )
