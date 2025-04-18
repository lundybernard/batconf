from unittest import TestCase

from dataclasses import dataclass
from typing import Dict, Optional

from ..source import SourceInterface, SourceList
from ..manager import Configuration, OpStr, _configuration_repr


SRC = 'batconf.manager'


class Source(SourceInterface):
    def __init__(self, data: Dict[str, str]):
        self._data = data

    def get(self, key: str, path: OpStr = None) -> Optional[str]:
        return self._data.get(f'{path}.{key}', None)


class TestConfiguration(TestCase):
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
        t.assertRegex(
            str(t.conf),
            "Root <class 'bat"
            ".TestConfiguration.setUp.<locals>.GlobalConfig'>:\n"
            "    |- AModule <class 'bat.AModule"
            ".TestConfiguration.setUp.<locals>.ConfA'>:\n"
            '    |    |- no_default_arg: "MISSING_VALUE"\n'
            '    |    |- default_arg: "unused default value"\n'
            '    |    |- arg_1: "s1_a_arg_1"\n'
            "    |    |- SubModule <class 'bat.AModule.SubModule"
            ".TestConfiguration.setUp.<locals>.ConfSubModule'>:\n"
            '    |    |    |- arg_1: "s1_a_sub_1"\n'
            "    |- b_module <class 'bat.b_module"
            ".TestConfiguration.setUp.<locals>.BClient.Config'>:\n"
            '    |    |- arg_1: "s1_b_arg_1"\n'
            'SourceList=\\[\n'
            r'    <batconf.tests.manager_test.Source object at .*>,\n'
            r'    <batconf.tests.manager_test.Source object at .*>,\n'
            '\\]',
        )

        with t.subTest('child configuration to str'):
            module_path = f'{__name__}.TestConfiguration.setUp.<locals>'
            t.assertRegex(
                str(t.conf.AModule),
                f"Root <class '{module_path}.ConfA'>:\n"
                '    |- no_default_arg: "MISSING_VALUE"\n'
                '    |- default_arg: "unused default value"\n'
                '    |- arg_1: "s1_a_arg_1"\n'
                f"    |- SubModule <class '{module_path}.ConfSubModule\n"
                '    |    |- arg_1: "s1_a_sub_1"'
                'path=bat.Amodule\n'
                'SourceList=\\[\n'
                r'    <batconf.tests.manager_test.Source object at .*>,\n'
                r'    <batconf.tests.manager_test.Source object at .*>,\n'
                '\\]',
            )

    def test___repr__(t):
        t.assertRegex(
            repr(t.conf),
            f'Configuration\\(source_list=SourceList\\('
            rf'sources=\[<{__name__}.Source object at .*>, '
            rf'<{__name__}.Source object at .*>\]\), '
            'config_class='
            f"<class '{__name__}.TestConfiguration.setUp.<locals>"
            ".GlobalConfig'>\\)",
        )

    def test__configuration_repr(t):
        repr_str_list = _configuration_repr(t.conf, level=0)
        t.assertListEqual(
            [
                f"- AModule <class '{__name__}"
                ".TestConfiguration.setUp.<locals>.ConfA'>:",
                '    |- no_default_arg: "MISSING_VALUE"',
                '    |- default_arg: "unused default value"',
                '    |- arg_1: "s1_a_arg_1"',
                f"    |- SubModule <class '{__name__}"
                ".TestConfiguration.setUp.<locals>.ConfSubModule'>:",
                '    |    |- arg_1: "s1_a_sub_1"',
                f"- b_module <class '{__name__}"
                ".TestConfiguration.setUp.<locals>.BClient.Config'>:",
                '    |- arg_1: "s1_b_arg_1"',
            ],
            repr_str_list,
        )

    def test__configuration_repr_level1(t):
        """Adding a level indents the returned strings and adds a pipe char"""
        t.maxDiff = None
        repr_str_list = _configuration_repr(t.conf, level=1)
        t.assertListEqual(
            [
                f"    |- AModule <class '{__name__}"
                ".TestConfiguration.setUp.<locals>.ConfA'>:",
                '    |    |- no_default_arg: "MISSING_VALUE"',
                '    |    |- default_arg: "unused default value"',
                '    |    |- arg_1: "s1_a_arg_1"',
                f"    |    |- SubModule <class '{__name__}"
                ".TestConfiguration.setUp.<locals>.ConfSubModule'>:",
                '    |    |    |- arg_1: "s1_a_sub_1"',
                f"    |- b_module <class '{__name__}"
                ".TestConfiguration.setUp.<locals>.BClient.Config'>:",
                '    |    |- arg_1: "s1_b_arg_1"',
            ],
            repr_str_list,
        )

    def test__module(t):
        """the _module attribute is the __module__ of the config_class"""
        t.assertEqual(t.conf._module, t.GlobalConfig.__module__)
