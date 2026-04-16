import warnings
from unittest import TestCase
from unittest.mock import sentinel

from .._compat import make_deprecated_getattr


SRC = 'batconf.sources._compat'


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
