from unittest import TestCase
from unittest.mock import patch

from ..env import EnvConfig


SRC = 'batconf.sources.env'


class TestEnvConfig(TestCase):

    @patch.dict(
        f'{SRC}.os.environ',
        {
            'BAT_CONFIG_FILE': 'example.config.yaml',
            'BAT_MODULE_KEY': 'value',
            'BAT_MODULE_PATH_TO_KEY': 'value2',
        }
    )
    def test_get(t):
        conf = EnvConfig()

        with t.subTest('single key'):
            t.assertEqual(conf.get('config_file'), 'example.config.yaml')

        with t.subTest('missing value'):
            t.assertEqual(conf.get('remote_host'), None)

        with t.subTest('module value'):
            t.assertEqual(conf.get('key', module='bat.module'), 'value')

        with t.subTest('module and key paths'):
            t.assertEqual(
                conf.get('to.key', module='bat.module.path'),
                'value2'
            )

    def test_env_name(t):
        conf = EnvConfig()

        with t.subTest('single key'):
            t.assertEqual(conf.env_name('key'), 'BAT_KEY')

        with t.subTest('path key'):
            t.assertEqual(conf.env_name('path.to.key'), 'BAT_PATH_TO_KEY')

        with t.subTest('single key from module'):
            t.assertEqual(
                conf.env_name('key', module='bat.module'),
                'BAT_MODULE_KEY'
            )

        with t.subTest('module and key paths'):
            t.assertEqual(
                conf.env_name('to.key', module='bat.module.path'),
                'BAT_MODULE_PATH_TO_KEY'
            )
