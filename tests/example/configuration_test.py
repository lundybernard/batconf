from unittest import TestCase

from dataclasses import dataclass

from batconf.manager import Configuration, SourceList


class FreeFormConfigTreeTests(TestCase):

    def test_freeform_config_tree(t) -> None:

        @dataclass
        class Level2ConfigA:
            value: str = 'level 2 config A value'

        @dataclass
        class Level2ConfigB:
            value: str = 'level 2 config B value'

        @dataclass
        class Level1ConfigA:
            l2a: Level2ConfigA
            l2b: Level2ConfigB
            value: str = 'level 1 config A value'

        @dataclass
        class Level1ConfigB:
            l2a: Level2ConfigA
            l2b: Level2ConfigB
            value: str = 'level 1 config B value'

        @dataclass
        class RootConfig:
            l1a: Level1ConfigA
            l1b: Level1ConfigB
            nodefault: str
            value: str = 'root config value'

        cfg = Configuration(
            source_list=SourceList([]),
            config_class=RootConfig,
            path='root',
        )

        t.assertIsInstance(cfg, Configuration)
        t.assertEqual(cfg.value, 'root config value')
        t.assertIsInstance(cfg.l1a, Configuration)
        t.assertEqual(cfg.l1a.value, 'level 1 config A value')
        t.assertIsInstance(cfg.l1a.l2a, Configuration)
        t.assertEqual(cfg.l1a.l2a.value, 'level 2 config A value')
        t.assertIsInstance(cfg.l1a.l2a, Configuration)
        t.assertEqual(cfg.l1b.l2b.value, 'level 2 config B value')

        t.assertEqual(cfg.l1b.value, 'level 1 config B value')
        t.assertEqual(cfg.l1b.l2a.value, 'level 2 config A value')
        t.assertEqual(cfg.l1b.l2b.value, 'level 2 config B value')

        with t.assertRaises(AttributeError):
            cfg.nodefault


    def test_root_config_values(t) -> None:
        from os import path
        # Get the absolute path to the test config.yaml file
        example_dir = path.dirname(path.realpath(__file__))
        config_file_name = path.join(example_dir, "config.yaml")

        from batconf.sources.file import  FileConfig
        source_list = SourceList([
            FileConfig(
                config_file_name=config_file_name,
                config_env='flatfile',
            )
        ])

        @dataclass
        class FlatConfig:
            opt2: str
            opt3: str = 'opt3 default'

        cfg = Configuration(
            source_list=source_list,
            config_class=FlatConfig,
            path='application',
        )

        # LB: without specifying a path, the root path is 'configuration_test'
        # print(f'{cfg._path=}')

        t.assertEqual(cfg.opt1, 'flat file option 1')
        with t.assertRaises(AttributeError):
            t.assertEqual(cfg.opt2, 'sir not appearing in this film')

        t.assertEqual(cfg.opt3, 'opt3 default')
