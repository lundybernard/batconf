import warnings
from unittest import TestCase

from batconf import EnvSource
import batconf.sources.env as env_module


class EnvSourceTests(TestCase):
    """Integration tests for batconf.sources.env.EnvSource."""

    def test___repr__(t) -> None:
        with t.subTest('an undeclared prefix prints no argument, no warning'):
            es = EnvSource()

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                ret = repr(es)

            t.assertEqual('EnvSource()', ret)
            t.assertEqual([], caught)

        with t.subTest('a declared prefix prints quoted'):
            es = EnvSource(prefix='mytool')
            ret = repr(es)
            t.assertEqual("EnvSource(prefix='mytool')", ret)

        with t.subTest('prefix=None prints None'):
            es = EnvSource(prefix=None)
            ret = repr(es)
            t.assertEqual('EnvSource(prefix=None)', ret)


class EnvConfigDeprecationTests(TestCase):
    """EnvConfig is the pre-0.4 name for EnvSource."""

    def test___getattr__(t):
        with t.subTest('warns and names the replacement'):
            with t.assertWarns(DeprecationWarning) as cm:
                alias = env_module.__getattr__('EnvConfig')
            t.assertEqual(
                "'EnvConfig' is deprecated and will be removed in v0.5.0; "
                "use 'EnvSource' instead.",
                str(cm.warning),
            )

        with t.subTest('resolves to the renamed class'):
            t.assertIs(alias, env_module.EnvSource)


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
