"""Verify the public batconf.types namespace."""
import warnings
from unittest import TestCase

import batconf.types as types


class BatconfTypesTests(TestCase):
    """Verify all intended symbols are importable from batconf.types."""

    def test_protocols(t):
        t.assertTrue(hasattr(types, 'ConfigP'))
        t.assertTrue(hasattr(types, 'FieldP'))
        t.assertTrue(hasattr(types, 'SourceInterfaceP'))
        t.assertTrue(hasattr(types, 'SourceListP'))

    def test_deprecated_names(t):
        """Old Protocol/Proto-suffixed names emit DeprecationWarning but still resolve."""
        deprecated = {
            'ConfigProtocol': types.ConfigP,
            'FieldProtocol': types.FieldP,
            'SourceInterfaceProto': types.SourceInterfaceP,
            'SourceListProto': types.SourceListP,
        }
        for old_name, expected in deprecated.items():
            with t.subTest(old_name):
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter('always')
                    alias = getattr(types, old_name)
                t.assertIs(alias, expected)
                t.assertEqual(len(w), 1)
                t.assertIn(old_name, str(w[0].message))
                t.assertIs(w[0].category, DeprecationWarning)

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
