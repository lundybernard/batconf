from unittest import TestCase
from unittest.mock import Mock, patch, sentinel

from dataclasses import dataclass

from ..lib import ConfigSingleton, insert_source, Configuration


SRC = 'batconf.lib'


def get_config():
    """get_config always returns a new Configuration instance"""
    return Mock(key1='+value1+')


class ConfigSingletonTests(TestCase):
    def setUp(t):
        t.cs = ConfigSingleton(get_config_fn=get_config)

    def test___getattr__(t) -> None:
        t.assertEqual('+value1+', t.cs.key1)

    def test__reset(t) -> None:
        # get a value from the underlying Configuration instance
        value = t.cs.key
        # resetting the proxy replaces the underlying Configuration instance
        t.cs._reset()
        # So "key" is no longer the same object
        t.assertIsNot(value, t.cs.key)

    def test___str__(t):
        """__str__ provided by the Configuration object"""
        t.assertEqual(str(t.cs), str(t.cs._cfg))

    def test___repr__(t):
        """__repr__ is provided by the Configuration object"""
        t.assertEqual(repr(t.cs), repr(t.cs._cfg))


class InsertSourceTests(TestCase):
    @patch(f'{SRC}.SourceList', autospec=True)
    def setUp(t, SourceList: Mock):
        @dataclass
        class ConfigSchema:
            arg_1: str

        t.source_list = SourceList(sources=[])
        t.cfg = Configuration(
            config_class=ConfigSchema, source_list=t.source_list
        )
        t.source_0 = sentinel.source

    def test_insert_source_default(t) -> None:
        insert_source(cfg=t.cfg, source=t.source_0)
        t.source_list.insert_source.assert_called_with(
            source=t.source_0, index=0
        )

    def test_insert_source_index(t) -> None:
        insert_source(cfg=t.cfg, source=t.source_0, index=77)
        t.source_list.insert_source.assert_called_with(
            source=t.source_0, index=77
        )
