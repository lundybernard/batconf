from unittest import TestCase

from dataclasses import dataclass
from typing import Dict, Optional

from ..source import SourceInterface, SourceList
from ..manager import Configuration, OpStr, _configuration_repr


SRC = 'batconf.configuration.manager'


class Source(SourceInterface):
    def __init__(self, data: Dict[str, str]):
        self._data = data

    def get(self, key: str, path: OpStr = None) -> Optional[str]:
        if v := self._data.get(f'{path}.{key}'):
            return v
        return None


class TestConfiguration(TestCase):
    def setUp(t) -> None:
        """Values are looked up exclusively from the Source List"""
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

        """Config dataclasses are used to build the tree-structure,
        so attribute lookup will work.
        In this context only the attributes contain Config dataclasses are used
        """

        @dataclass
        class ConfSubModule:
            arg_1: str

        @dataclass
        class ConfA:
            SubModule: ConfSubModule
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

        #  As if imported from a module
        GlobalConfig.__module__ = 'bat'
        ConfA.__module__ = 'bat.AModule'
        BClient.Config.__module__ = 'bat.b_module'
        ConfSubModule.__module__ = 'bat.AModule.SubModule'

        t.GlobalConfig = GlobalConfig

        t.conf = Configuration(t.source_list, t.GlobalConfig)

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

        with t.subTest('defaults from Config classes are not available'):
            with t.assertRaises(AttributeError):
                t.conf.AModule.default_arg

    def test___getattr__(t) -> None:
        with t.subTest('module lookup'):
            t.assertEqual(t.conf.AModule.s1_unique, 's1_a_unique')

        with t.subTest('sub-module lookup'):
            t.assertEqual(t.conf.AModule.SubModule.arg_1, 's1_a_sub_1')

        with t.subTest('__getattr__ missing'):
            with t.assertRaises(AttributeError):
                t.conf._sir_not_appearing_in_this_film

    def test___str__(t):
        t.assertRegex(
            str(t.conf),
            "Root <class 'bat"
            ".TestConfiguration.setUp.<locals>.GlobalConfig'>:\n"
            "    |- AModule <class 'bat.AModule"
            ".TestConfiguration.setUp.<locals>.ConfA'>:\n"
            '    |    |- default_arg: "MISSING_VALUE"\n'
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

        # TODO: Fix bug, this should work but fails to find the attribute
        with t.assertRaises(AttributeError):
            t.assertRegex(
                str(t.conf.ConfA),
                '- AModule\n'
                '   └─ SubModule\n'
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
            f'<{__name__}'
            r'.Source object at .*>\]\), '
            'config_class='
            "<class 'bat.TestConfiguration.setUp.<locals>.GlobalConfig'>\\)",
        )

    def test__configuration_repr(t):
        repr_str_list = _configuration_repr(t.conf, level=0)
        t.assertListEqual(
            [
                "- AModule <class 'bat.AModule"
                ".TestConfiguration.setUp.<locals>.ConfA'>:",
                '    |- default_arg: "MISSING_VALUE"',
                '    |- arg_1: "s1_a_arg_1"',
                "    |- SubModule <class 'bat.AModule.SubModule"
                ".TestConfiguration.setUp.<locals>.ConfSubModule'>:",
                '    |    |- arg_1: "s1_a_sub_1"',
                "- b_module <class 'bat.b_module"
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
                "    |- AModule <class 'bat.AModule"
                ".TestConfiguration.setUp.<locals>.ConfA'>:",
                '    |    |- default_arg: "MISSING_VALUE"',
                '    |    |- arg_1: "s1_a_arg_1"',
                "    |    |- SubModule <class 'bat.AModule.SubModule"
                ".TestConfiguration.setUp.<locals>.ConfSubModule'>:",
                '    |    |    |- arg_1: "s1_a_sub_1"',
                "    |- b_module <class 'bat.b_module"
                ".TestConfiguration.setUp.<locals>.BClient.Config'>:",
                '    |    |- arg_1: "s1_b_arg_1"',
            ],
            repr_str_list,
        )
