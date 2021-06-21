from unittest import TestCase

from dataclasses import dataclass

from ..source import SourceInterface, SourceList
from ..manager import Configuration


SRC = 'bat.configuration.manager'


class Source(SourceInterface):
    def __init__(self, data):
        self._data = data

    def get(self, key: str, path: str = None):
        if v := self._data.get(f'{path}.{key}'):
            return v
        return None


class TestConfiguration(TestCase):

    def setUp(t):
        '''Values are looked up exclusively from the Source List
        '''
        t.source_1 = Source({
            'bat.AModule.arg_1': 's1_a_arg_1',
            'bat.AModule.s1_unique': 's1_a_unique',
            'bat.AModule.SubModule.arg_1': 's1_a_sub_1',
            'bat.BModule.arg_1': 's1_b_arg_1',
            'bat.BModule.s1_unique': 's1_b_unique'
        })
        t.source_2 = Source({
            'bat.AModule.arg_1': 's2_a_arg_1',
            'bat.AModule.arg_2': 's2_a_arg_2',
            'bat.AModule.s2_unique': 's2_a_unique',
            'bat.AModule.SubModule.arg_1': 's2_a_sub_1',
            'bat.BModule.arg_1': 's2_b_arg_1',
            'bat.BModule.s2_unique': 's2_b_unique'
        })
        t.source_list = SourceList([t.source_1, t.source_2])

        '''Config dataclasses are used to build the tree-structure,
        so attribute lookup will work.
        In this context only the attributes contain Config dataclasses are used
        '''
        @dataclass
        class ConfSubModule:
            arg_1: str

        @dataclass
        class ConfA:
            SubModule: ConfSubModule
            default_arg: str = 'unused default value'

        @dataclass
        class ConfB:
            arg_1: str

        @dataclass
        class GlobalConfig:
            AModule: ConfA
            BModule: ConfB

        #  As if imported from a module
        GlobalConfig.__module__ = 'bat'
        ConfA.__module__ = 'bat.AModule'
        ConfB.__module__ = 'bat.BModule'
        ConfSubModule.__module__ = 'bat.AModule.SubModule'

        t.GlobalConfig = GlobalConfig

        t.conf = Configuration(t.source_list, t.GlobalConfig)

    def test_from_sources(t):
        with t.subTest('get value from first source'):
            t.assertEqual(t.conf.AModule.s1_unique, 's1_a_unique')
            t.assertEqual(t.conf.BModule.s1_unique, 's1_b_unique')

        with t.subTest('get value from n+1 source'):
            t.assertEqual(t.conf.AModule.s2_unique, 's2_a_unique')
            t.assertEqual(t.conf.BModule.s2_unique, 's2_b_unique')

    def test_configuration_priority(t):
        with t.subTest('first source is top priority'):
            t.assertEqual(t.conf.AModule.arg_1, 's1_a_arg_1')

        with t.subTest('source n+1 is nexttop priority'):
            t.assertEqual(t.conf.AModule.arg_2, 's2_a_arg_2')

        with t.subTest('defaults from Config classes are not available'):
            with t.assertRaises(AttributeError):
                t.conf.AModule.default_arg

    def test___getattr__(t):

        with t.subTest('module lookup'):
            t.assertEqual(t.conf.AModule.s1_unique, 's1_a_unique')

        with t.subTest('sub-module lookup'):
            t.assertEqual(t.conf.AModule.SubModule.arg_1, 's1_a_sub_1')

        with t.subTest('__getattr__ missing'):
            with t.assertRaises(AttributeError):
                t.conf._sir_not_appearing_in_this_film
