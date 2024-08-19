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
