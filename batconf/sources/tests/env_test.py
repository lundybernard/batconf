from unittest import TestCase
from unittest.mock import patch

from ..env import EnvSource


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

        with t.subTest('no prefix declares no namespace'):
            source = EnvSource()
            t.assertEqual(source.env_name('key', path='server'), 'SERVER_KEY')
            t.assertEqual(source.env_name('key'), 'KEY')

    def test___str__(t) -> None:
        t.assertEqual(f'Environment Variables: {repr(t.es)}', str(t.es))

    def test___repr__(t) -> None:
        t.assertEqual('EnvSource()', repr(t.es))


class BareNameGuardTests(TestCase):
    """Without a namespace, a root lookup reads no ambient variable."""

    def setUp(t) -> None:
        t.es = EnvSource()  # no prefix: bare names are guarded
        t.es_raw = EnvSource(raw=True)

    @patch.dict(
        f'{SRC}.os.environ',
        {
            'VALUE': 'an ambient process variable',
            'SERVER_HOST': 'localhost',
            'MYTOOL_VALUE': 'a namespaced value',
        },
    )
    def test_get(t):
        with t.subTest('an empty path and no prefix resolves nothing'):
            t.assertIsNone(t.es.get('value'))

        with t.subTest('a path resolves without a prefix'):
            t.assertEqual('localhost', t.es.get('host', path='server'))

        with t.subTest('raw=True lifts the guard'):
            t.assertEqual('an ambient process variable', t.es_raw.get('value'))

        with t.subTest('a prefix lifts the guard'):
            source = EnvSource(prefix='mytool')
            t.assertEqual('a namespaced value', source.get('value'))
