from unittest import TestCase
from unittest.mock import Mock, patch, sentinel

from dataclasses import dataclass

from ..lib import insert_source, Configuration


SRC = 'batconf.lib'


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
