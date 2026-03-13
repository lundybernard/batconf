from unittest import TestCase

from ..argparse import NamespaceConfig, Namespace


class TestNamespaceConfig(TestCase):
    def test_get(t):
        cli_args = Namespace(
            config_file='example.config.yaml',
            key='value',
        )
        setattr(cli_args, 'path.style.opt', 'path-style-option')
        setattr(cli_args, 'bat.module.path.to.key', 'value')

        cs = NamespaceConfig(cli_args)

        with t.subTest('single key'):
            t.assertEqual(cs.get('config_file'), 'example.config.yaml')

        with t.subTest('path.style.key'):
            t.assertEqual(cs.get('path.style.opt'), 'path-style-option')

        with t.subTest('missing value'):
            t.assertEqual(cs.get('missing'), None)

        with t.subTest('module and key paths'):
            t.assertEqual(cs.get('to.key', module='bat.module.path'), 'value')

    def test___str__(t) -> None:
        cs = NamespaceConfig(Namespace())
        t.assertEqual(f'Namespace Source: {repr(cs)}', str(cs))

    def test___repr__(t) -> None:
        cs = NamespaceConfig(Namespace())
        t.assertEqual('NamespaceConfig(namespace=Namespace())', repr(cs))
