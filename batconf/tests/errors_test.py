from unittest import TestCase

from ..errors import (
    BatconfError,
    ConfigEnvironmentNotFound,
    ConfigFileNotFound,
    ConfigValueNotFound,
    InvalidFileFormat,
    SourceDependencyNotFound,
)


class ErrorHierarchyTests(TestCase):
    """Each error is a BatconfError and the exception it replaces."""

    def setUp(t) -> None:
        t.message = 'the failure'

    def test_ConfigFileNotFound(t) -> None:
        err = ConfigFileNotFound(t.message)

        with t.subTest('BatconfError'):
            t.assertIsInstance(err, BatconfError)

        with t.subTest('FileNotFoundError'):
            t.assertIsInstance(err, FileNotFoundError)

    def test_ConfigEnvironmentNotFound(t) -> None:
        err = ConfigEnvironmentNotFound(t.message)

        with t.subTest('BatconfError'):
            t.assertIsInstance(err, BatconfError)

        with t.subTest('ValueError'):
            t.assertIsInstance(err, ValueError)

    def test_InvalidFileFormat(t) -> None:
        err = InvalidFileFormat(t.message)

        with t.subTest('BatconfError'):
            t.assertIsInstance(err, BatconfError)

        with t.subTest('ValueError'):
            t.assertIsInstance(err, ValueError)

    def test_ConfigValueNotFound(t) -> None:
        err = ConfigValueNotFound(t.message)

        with t.subTest('BatconfError'):
            t.assertIsInstance(err, BatconfError)

        with t.subTest('AttributeError'):
            t.assertIsInstance(err, AttributeError)

    def test_SourceDependencyNotFound(t) -> None:
        err = SourceDependencyNotFound(t.message)

        with t.subTest('BatconfError'):
            t.assertIsInstance(err, BatconfError)

        with t.subTest('ImportError'):
            t.assertIsInstance(err, ImportError)

        with t.subTest('ImportError.msg'):
            t.assertEqual(err.msg, t.message)
