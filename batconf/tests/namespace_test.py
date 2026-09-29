"""Verify the public batconf root namespace."""
from unittest import TestCase

import batconf


class BatconfNamespaceTests(TestCase):
    """Verify all intended symbols are importable from the root namespace."""

    def test_core(t):
        t.assertTrue(hasattr(batconf, 'Configuration'))
        t.assertTrue(hasattr(batconf, 'ConfigSingleton'))
        t.assertTrue(hasattr(batconf, 'SourceList'))
        t.assertTrue(hasattr(batconf, 'insert_source'))

    def test_sources(t):
        t.assertTrue(hasattr(batconf, 'NamespaceSource'))
        t.assertTrue(hasattr(batconf, 'Namespace'))
        t.assertTrue(hasattr(batconf, 'EnvSource'))
        t.assertTrue(hasattr(batconf, 'IniSource'))
        t.assertTrue(hasattr(batconf, 'TomlSource'))
        t.assertTrue(hasattr(batconf, 'YamlSource'))

    def test_errors(t):
        t.assertTrue(hasattr(batconf, 'BatconfError'))
        t.assertTrue(hasattr(batconf, 'ConfigEnvironmentNotFound'))
        t.assertTrue(hasattr(batconf, 'ConfigFileNotFound'))
        t.assertTrue(hasattr(batconf, 'ConfigValueNotFound'))
        t.assertTrue(hasattr(batconf, 'InvalidFileFormat'))
        t.assertTrue(hasattr(batconf, 'SourceDependencyNotFound'))

    def test_all_is_complete(t):
        """Every symbol in __all__ must be importable from batconf."""
        for name in batconf.__all__:
            t.assertTrue(
                hasattr(batconf, name),
                msg=f'batconf.__all__ lists {name!r} but it is not importable',
            )

