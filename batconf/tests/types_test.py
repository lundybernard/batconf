"""Verify the public batconf.types namespace."""
from unittest import TestCase

import batconf.types as types


class BatconfTypesTests(TestCase):
    """Verify all intended symbols are importable from batconf.types."""

    def test_protocols(t):
        t.assertTrue(hasattr(types, 'ConfigProtocol'))
        t.assertTrue(hasattr(types, 'SourceInterfaceProto'))
        t.assertTrue(hasattr(types, 'SourceListProto'))

    def test_type_aliases(t):
        t.assertTrue(hasattr(types, 'ConfigFileFormats'))
        t.assertTrue(hasattr(types, 'MissingFileOption'))

    def test_all_is_complete(t):
        """Every symbol in __all__ must be importable from batconf.types."""
        for name in types.__all__:
            t.assertTrue(
                hasattr(types, name),
                msg=f'batconf.types.__all__ lists {name!r} but it is not importable',
            )
