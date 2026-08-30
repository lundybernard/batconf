import warnings
from unittest import TestCase

from .._compat import deprecated_module


SRC = 'batconf.sources._compat'


_MODULE_WARNING = (
    "the 'module' keyword argument to .get() is deprecated and will "
    "be removed in v0.5.0; use 'path' instead."
)


class DeprecatedModuleTests(TestCase):
    """``deprecated_module`` maps the deprecated ``module`` keyword of
    ``.get()`` onto its replacement ``path`` and warns when it is used."""

    def test_no_module_returns_path_silently(t):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            result = deprecated_module(path='a.b', module=None)
        t.assertEqual(result, 'a.b')
        t.assertEqual(len(w), 0)

    def test_module_only_returns_module_and_warns(t):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            result = deprecated_module(path=None, module='a.b')
        t.assertEqual(result, 'a.b')
        t.assertEqual(len(w), 1)
        t.assertIs(w[0].category, DeprecationWarning)
        t.assertEqual(_MODULE_WARNING, str(w[0].message))

    def test_method_names_the_deprecating_method(t):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            result = deprecated_module(
                path=None, module='a.b', method='env_name'
            )
        t.assertEqual(result, 'a.b')
        t.assertEqual(
            "the 'module' keyword argument to .env_name() is deprecated "
            "and will be removed in v0.5.0; use 'path' instead.",
            str(w[0].message),
        )

    def test_path_wins_when_both_supplied(t):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            result = deprecated_module(path='keep', module='ignore')
        t.assertEqual(result, 'keep')
        t.assertEqual(len(w), 1)
        t.assertIs(w[0].category, DeprecationWarning)
        t.assertEqual(_MODULE_WARNING, str(w[0].message))
