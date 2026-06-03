import warnings
from unittest import TestCase
from unittest.mock import sentinel

from .._compat import make_deprecated_getattr, deprecated_module


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

    def test_path_wins_when_both_supplied(t):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            result = deprecated_module(path='keep', module='ignore')
        t.assertEqual(result, 'keep')
        t.assertEqual(len(w), 1)
        t.assertIs(w[0].category, DeprecationWarning)
        t.assertEqual(_MODULE_WARNING, str(w[0].message))


class MakeDeprecatedGetAttrTests(TestCase):
    def setUp(t):
        t.module_globals = {'NewName': sentinel.NewClass}
        t.module_name = 'batconf.sources.somemodule'
        t.deprecated = {'OldName': 'NewName'}

        t.dga = make_deprecated_getattr(
            deprecated=t.deprecated,
            module_globals=t.module_globals,
            module_name=t.module_name,
        )

    def test_returns_new_class(t):
        with warnings.catch_warnings(record=True):
            result = t.dga('OldName')
        t.assertIs(result, sentinel.NewClass)

    def test_emits_deprecation_warning(t):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            t.dga('OldName')
        t.assertIs(w[0].category, DeprecationWarning)
        t.assertEqual(
            f"'OldName' is deprecated, use 'NewName' instead.",
            str(w[0].message)
            )

    def test_raises_attribute_error_for_unknown_name(t):
        with t.assertRaises(AttributeError) as err:
            t.dga('NonExistent')
        t.assertEqual(
            f"module '{t.module_name}' has no attribute 'NonExistent'",
            str(err.exception)
        )

    def test_targets_returns_different_object(t):
        """targets overrides which object is returned while keeping the
        display name in the warning message unchanged."""
        module_globals = {
            'NewName': sentinel.NewClass,
            '_LegacyClass': sentinel.LegacyClass,
        }
        dga = make_deprecated_getattr(
            deprecated={'OldName': 'NewName'},
            module_globals=module_globals,
            module_name=t.module_name,
            targets={'OldName': '_LegacyClass'},
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            result = dga('OldName')

        t.assertIs(result, sentinel.LegacyClass)
        t.assertEqual(
            "'OldName' is deprecated, use 'NewName' instead.",
            str(w[0].message),
        )
