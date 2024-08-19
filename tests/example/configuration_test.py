from unittest import TestCase

from dataclasses import dataclass

from batconf.manager import Configuration, SourceList
from batconf.sources.dataclass import DataclassConfig


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
            value: str = 'root config value'

        cfg = Configuration(
            source_list=SourceList(
                [
                    DataclassConfig(RootConfig, path='root'),
                ]
            ),
            config_class=RootConfig,
            path='root',
        )

        t.assertEqual(cfg.value, 'root config value')
        t.assertEqual(cfg.l1a.value, 'level 1 config A value')
        t.assertEqual(cfg.l1a.l2a.value, 'level 2 config A value')
        t.assertEqual(cfg.l1b.l2b.value, 'level 2 config B value')

        t.assertIsInstance(cfg.l1a.l2a, Configuration)
        t.assertEqual(cfg.l1b.value, 'level 1 config B value')
        t.assertEqual(cfg.l1b.l2a.value, 'level 2 config A value')
        t.assertEqual(cfg.l1b.l2b.value, 'level 2 config B value')
