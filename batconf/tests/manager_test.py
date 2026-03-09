from unittest import TestCase

from dataclasses import dataclass

from ..manager import Configuration, _configuration_repr, SourceList


SRC = 'batconf.manager'


class Source:
    def __init__(self, data: dict[str, str]):
        self._data = data

    def get(self, key: str, path: str | None = None) -> str | None:
        return self._data.get(f'{path}.{key}', None)


class ConfigurationTests(TestCase):
    def setUp(t) -> None:
        """Configuration parameters/values are looked up from the Source List"""
        t.source_1 = Source(
            {
                'bat.AModule.arg_1': 's1_a_arg_1',
                'bat.AModule.s1_unique': 's1_a_unique',
                'bat.AModule.SubModule.arg_1': 's1_a_sub_1',
                'bat.b_module.arg_1': 's1_b_arg_1',
                'bat.b_module.s1_unique': 's1_b_unique',
            }
        )
        t.source_2 = Source(
            {
                'bat.AModule.arg_1': 's2_a_arg_1',
                'bat.AModule.arg_2': 's2_a_arg_2',
                'bat.AModule.s2_unique': 's2_a_unique',
                'bat.AModule.SubModule.arg_1': 's2_a_sub_1',
                'bat.b_module.arg_1': 's2_b_arg_1',
                'bat.b_module.s2_unique': 's2_b_unique',
            }
        )
        t.source_list = SourceList([t.source_1, t.source_2])

        """
        Config dataclasses are used to build the tree-structure,
        so attribute lookup will work.
        In this context only the attributes contain Config dataclasses are used
        """

        @dataclass
        class ConfSubModule:
            arg_1: str

        @dataclass
        class ConfA:
            SubModule: ConfSubModule
            no_default_arg: str
            default_arg: str = 'unused default value'
            arg_1: str = 'ConfA arg_1 default'

        class BClient:
            @dataclass
            class Config:
                arg_1: str

        @dataclass
        class GlobalConfig:
            AModule: ConfA
            b_module: BClient.Config

        t.GlobalConfig = GlobalConfig

        t.conf = Configuration(t.source_list, t.GlobalConfig, path='bat')

        t.mod = f'{__name__}.ConfigurationTests.setUp.<locals>'

    def test_from_sources(t) -> None:
        with t.subTest('get value from first source'):
            t.assertEqual(t.conf.AModule.s1_unique, 's1_a_unique')
            t.assertEqual(t.conf.b_module.s1_unique, 's1_b_unique')

        with t.subTest('get value from n+1 source'):
            t.assertEqual(t.conf.AModule.s2_unique, 's2_a_unique')
            t.assertEqual(t.conf.b_module.s2_unique, 's2_b_unique')

    def test_configuration_priority(t) -> None:
        with t.subTest('first source is top priority'):
            t.assertEqual(t.conf.AModule.arg_1, 's1_a_arg_1')

        with t.subTest('source n+1 is next top priority'):
            t.assertEqual(t.conf.AModule.arg_2, 's2_a_arg_2')

        with t.subTest('default values from Config classes'):
            t.assertEqual(t.conf.AModule.default_arg, 'unused default value')

        with t.subTest('options without defaults raise AttributeError'):
            with t.assertRaises(AttributeError):
                t.conf.AModule.no_default_arg

    def test___getattr__(t) -> None:
        with t.subTest('module lookup'):
            t.assertEqual(t.conf.AModule.s1_unique, 's1_a_unique')

        with t.subTest('child configurations'):
            """Child configurations are Configuration instances
            """
            t.assertIsInstance(t.conf.AModule, Configuration)

        with t.subTest('sub-module value lookup'):
            t.assertEqual(t.conf.AModule.SubModule.arg_1, 's1_a_sub_1')

        with t.subTest('__getattr__ missing'):
            with t.assertRaises(AttributeError):
                t.conf._sir_not_appearing_in_this_film

        with t.subTest(
            'options with no value and no default raise AttributeError'
        ):
            with t.assertRaises(AttributeError):
                t.conf.AModule.no_default_arg

    def test___str__(t):
        exp = (
            f"bat <class '{t.mod}.GlobalConfig'>:\n"
            f"    |- AModule <class '{t.mod}.ConfA'>:\n"
            '    |    |- no_default_arg: "MISSING_VALUE"\n'
            '    |    |- default_arg: "unused default value"\n'
            '    |    |- arg_1: "s1_a_arg_1"\n'
            f"    |    |- SubModule <class '{t.mod}.ConfSubModule'>:\n"
            '    |    |    |- arg_1: "s1_a_sub_1"\n'
            f"    |- b_module <class '{t.mod}.BClient.Config'>:\n"
            '    |    |- arg_1: "s1_b_arg_1"\n'
            'SourceList=[\n'
            f'    {repr(t.source_1)},\n'
            f'    {repr(t.source_2)},\n'
            ']'
        )

        t.assertEqual(str(t.conf), exp)

        with t.subTest('child configuration to str'):
            t.assertEqual(
                f"bat.AModule <class '{t.mod}.ConfA'>:\n"
                '    |- no_default_arg: "MISSING_VALUE"\n'
                '    |- default_arg: "unused default value"\n'
                '    |- arg_1: "s1_a_arg_1"\n'
                f"    |- SubModule <class '{t.mod}.ConfSubModule'>:\n"
                '    |    |- arg_1: "s1_a_sub_1"\n'
                'SourceList=[\n'
                f'    {repr(t.source_1)},\n'
                f'    {repr(t.source_2)},\n'
                ']',
                str(t.conf.AModule),
            )

    def test___repr__(t):
        t.assertEqual(
            'Configuration(source_list=SourceList('
            f'sources=[{t.source_1}, {t.source_2}]), '
            f"config_class=<class '{t.mod}.GlobalConfig'>)",
            repr(t.conf),
        )

    def test__configuration_repr(t):
        repr_str_list = _configuration_repr(t.conf, level=0)
        t.assertListEqual(
            [
                f"- AModule <class '{t.mod}.ConfA'>:",
                '    |- no_default_arg: "MISSING_VALUE"',
                '    |- default_arg: "unused default value"',
                '    |- arg_1: "s1_a_arg_1"',
                f"    |- SubModule <class '{t.mod}.ConfSubModule'>:",
                '    |    |- arg_1: "s1_a_sub_1"',
                f"- b_module <class '{t.mod}.BClient.Config'>:",
                '    |- arg_1: "s1_b_arg_1"',
            ],
            repr_str_list,
        )

    def test__configuration_repr_level1(t):
        """Adding a level indents the returned strings and adds a pipe char"""
        repr_str_list = _configuration_repr(t.conf, level=1)
        t.assertListEqual(
            [
                f"    |- AModule <class '{t.mod}.ConfA'>:",
                '    |    |- no_default_arg: "MISSING_VALUE"',
                '    |    |- default_arg: "unused default value"',
                '    |    |- arg_1: "s1_a_arg_1"',
                f"    |    |- SubModule <class '{t.mod}.ConfSubModule'>:",
                '    |    |    |- arg_1: "s1_a_sub_1"',
                f"    |- b_module <class '{t.mod}.BClient.Config'>:",
                '    |    |- arg_1: "s1_b_arg_1"',
            ],
            repr_str_list,
        )

    def test__module(t):
        """the _module attribute is the __module__ of the config_class"""
        t.assertEqual(t.conf._module, t.GlobalConfig.__module__)
