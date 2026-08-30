import warnings
from unittest import TestCase

from batconf import EnvSource


class EnvNameModuleDeprecationTests(TestCase):
    """module= is the pre-0.4 name for env_name's path argument."""

    def setUp(t) -> None:
        t.es = EnvSource(prefix='mytool')

    def test_env_name(t):
        with t.subTest('module= builds the name and warns'):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                via_module = t.es.env_name('key', module='server')
            t.assertEqual('MYTOOL_SERVER_KEY', via_module)
            t.assertEqual(1, len(caught))
            t.assertIs(caught[0].category, DeprecationWarning)
            t.assertEqual(
                "the 'module' keyword argument to .env_name() is "
                "deprecated and will be removed in v0.5.0; use 'path' "
                'instead.',
                str(caught[0].message),
            )

        with t.subTest('path= builds the same name, no warning'):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                via_path = t.es.env_name('key', path='server')
            t.assertEqual('MYTOOL_SERVER_KEY', via_path)
            t.assertEqual([], caught)
