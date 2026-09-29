"""Verify the public batconf.sources.types namespace."""
from unittest import TestCase

from .. import types


class SourcesTypesTests(TestCase):
    """Verify all intended symbols are importable from batconf.sources.types."""

    def test_type_aliases(t):
        t.assertTrue(hasattr(types, 'ConfigFileFormats'))
        t.assertTrue(hasattr(types, 'MissingFileOption'))

    def test_protocols(t):
        t.assertTrue(hasattr(types, 'SourceInterfaceP'))
        t.assertTrue(hasattr(types, 'FileSourceP'))

    def test_runtime_checkable(t):
        """The protocols answer isinstance, so a custom source can be
        checked without inheriting from anything."""

        class Source:
            def get(self, key: str, path: str | None = None) -> None: ...

        with t.subTest('SourceInterfaceP instance'):
            t.assertIsInstance(Source(), types.SourceInterfaceP)

        with t.subTest('SourceInterfaceP subclass'):
            t.assertTrue(issubclass(Source, types.SourceInterfaceP))

        with t.subTest('FileSourceP instance'):
            t.assertIsInstance(Source(), types.FileSourceP)

    def test_all_is_complete(t):
        """Every symbol in __all__ must be importable from batconf.sources.types."""
        for name in types.__all__:
            t.assertTrue(
                hasattr(types, name),
                msg=f'batconf.sources.types.__all__ lists {name!r} but it is not importable',
            )
