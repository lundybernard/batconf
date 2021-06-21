from unittest import TestCase

from ..dataclass import DataclassConfig, dataclass


class TestDataclassConfig(TestCase):

    def test_get(t):
        @dataclass
        class SubConfig:
            key: str = 'sub_v_1'

        SubConfig.__module__ = 'bat.TestModule.SubModule'

        @dataclass
        class ConfigClass:
            remote_host: dict
            SubModule: SubConfig
            key: str = 'v_1'

        ConfigClass.__module__ = 'bat.TestModule'

        @dataclass
        class GlobalConfig:
            TestModule: ConfigClass
            config_file: str = './GlobalConfig.yaml'

        GlobalConfig.__module__ = 'bat'

        conf = DataclassConfig(GlobalConfig)

        with t.subTest('single key'):
            t.assertEqual(conf.get('config_file'), './GlobalConfig.yaml')

        with t.subTest('module value'):
            t.assertEqual(
                conf.get('key', module=ConfigClass.__module__),
                'v_1'
            )

        with t.subTest('key paths'):
            t.assertEqual(conf.get('TestModule.key',), 'v_1')
            t.assertEqual(conf.get('TestModule.SubModule.key',), 'sub_v_1')

        with t.subTest('module and key paths'):
            t.assertEqual(
                conf.get('key', module=SubConfig.__module__), 'sub_v_1'
            )
            t.assertEqual(
                conf.get('SubModule.key', module=ConfigClass.__module__),
                'sub_v_1'
            )

        with t.subTest('missing value'):
            t.assertEqual(conf.get('missing'), None)

        with t.subTest('missing default value'):
            t.assertEqual(conf.get('TestModule.remote_host'), None)
