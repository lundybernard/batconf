from unittest import TestCase

from dataclasses import dataclass

from ..source import (
    SourceList,
    SourceInterface,
    OpStr,
)


class TestSourceInterfaceABC(TestCase):
    def test_config_source_interface(t):
        SourceInterface.__abstractmethods__ = set()

        @dataclass
        class Source(SourceInterface):
            pass

        cs = Source()
        t.assertEqual(cs.get('key', path='bat.path'), None)


class Source(SourceInterface):
    def __init__(self, data):
        self._data = data

    def get(self, key: str, path: OpStr = None):
        if v := self._data.get(f'{path}.{key}'):
            return v
        return None


class TestSourceList(TestCase):
    def setUp(t):
        t.source_1 = Source({'p1.key1': 'value1'})
        t.source_2 = Source({'p2.key2': 'value2'})
        t.source_3 = Source({'p1.key1': 'value3'})

    def test_get(t):
        sl = SourceList([t.source_1, t.source_2])

        with t.subTest('get value from first source'):
            t.assertEqual(sl.get('key1', 'p1'), 'value1')

        with t.subTest('get value from n+1 source'):
            t.assertEqual(sl.get('key2', 'p2'), 'value2')

        with t.subTest('missing attribute returns None'):
            t.assertEqual(sl.get('DNE'), None)

    def test_none_values_in_args(t):
        """Given None values in the initial sources list,
        they will be ignored, and only valid sources used
        """
        sl = SourceList([None, t.source_1, None, t.source_2, None])
        t.assertEqual(sl.get('key2', 'p2'), 'value2')

    def test_get_priority(t):
        """If duplicate keys exist in multiple sources,
        always return the first found in the list
        """
        sl = SourceList([t.source_1, t.source_3])
        t.assertEqual(sl.get('key1', 'p1'), 'value1')

        sl = SourceList([t.source_3, t.source_1])
        t.assertEqual(sl.get('key1', 'p1'), 'value3')

    def test___str__(t):
        ret = str(SourceList([t.source_1, t.source_2]))
        t.assertRegex(
            ret,
            'SourceList=\\[\n'
            r'    <batconf.tests.source_test.Source object at 0x.+>,\n'
            r'    <batconf.tests.source_test.Source object at 0x.+>,\n'
            '\\]',
        )

    def test___repr__(t):
        ret = repr(SourceList([t.source_1, t.source_2]))
        t.assertRegex(
            ret,
            'SourceList\\(sources=\\['
            r'<batconf.tests.source_test.Source object at 0x.+>, '
            r'<batconf.tests.source_test.Source object at 0x.+>'
            '\\]\\)',
        )
