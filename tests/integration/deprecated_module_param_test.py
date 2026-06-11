"""The ``module`` keyword argument to ``Source.get()`` is deprecated.

``path`` replaces it (ADR 0002, issue #3). Until removal in v0.5.0, passing
``module=`` must still resolve the same value as ``path=`` but emit a
``DeprecationWarning``. This is the highest-level, outside-in specification:
it exercises the deprecation through the public source classes exactly as a
user would, independent of how any one source resolves a namespace.
"""
import warnings
from argparse import Namespace
from unittest import TestCase
from unittest.mock import patch

from batconf import EnvSource, NamespaceSource
from batconf.sources.dataclass import DataclassConfig


_MODULE_WARNING = (
    "the 'module' keyword argument to .get() is deprecated and will "
    "be removed in v0.5.0; use 'path' instead."
)


class DeprecatedModuleParameterTests(TestCase):
    def _assert_parity_and_warning(t, source, key, namespace, expected):
        """``module=namespace`` resolves ``expected`` and warns;
        ``path=namespace`` resolves the same value without warning."""
        with t.subTest('module= resolves the value and warns'):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                via_module = source.get(key, module=namespace)
            t.assertEqual(via_module, expected)
            deprecations = [
                w for w in caught
                if issubclass(w.category, DeprecationWarning)
            ]
            t.assertEqual(len(deprecations), 1)
            t.assertEqual(_MODULE_WARNING, str(deprecations[0].message))

        with t.subTest('path= resolves the same value, no warning'):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                via_path = source.get(key, path=namespace)
            t.assertEqual(via_path, expected)
            t.assertEqual(
                [w for w in caught
                 if issubclass(w.category, DeprecationWarning)],
                [],
            )

    @patch.dict('batconf.sources.env.os.environ', {'BAT_MODULE_KEY': 'value'})
    def test_env_source(t):
        t._assert_parity_and_warning(
            EnvSource(), key='key', namespace='bat.module', expected='value'
        )

    def test_namespace_source(t):
        ns = Namespace()
        setattr(ns, 'bat.module.key', 'value')
        t._assert_parity_and_warning(
            NamespaceSource(ns), key='key', namespace='bat.module',
            expected='value',
        )

    def test_dataclass_source(t):
        from dataclasses import dataclass

        @dataclass
        class Config:
            key: str = 'value'

        source = DataclassConfig(Config, path='bat.module')
        t._assert_parity_and_warning(
            source, key='key', namespace='bat.module', expected='value'
        )
