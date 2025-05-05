from unittest import TestCase

from batconf.sources.argparse import NamespaceConfig

from argparse import ArgumentParser, Namespace


def argparser(cfg_path='root'):
    p = ArgumentParser()
    p.add_argument('-a', dest=f'{cfg_path}.alpha')

    commands = p.add_subparsers(dest='command')
    commands.add_parser(
        'command1',
        parents=[command_cli(f'{cfg_path}.command1')],
        add_help=False,
    )
    # reusable sub-parser for commands
    commands.add_parser(
        'command2',
        parents=[command_cli(f'{cfg_path}.command2')],
        add_help=False,
    )

    return p


def command_cli(cfg_path: str):
    p = ArgumentParser()
    p.add_argument('--cmd-option', dest=f'{cfg_path}.opt')
    return p


class NamespaceSourceTests(TestCase):
    def test_(t) -> None:
        parser = argparser()
        args = ['-a=value_a', 'command1', '--cmd-option=co1']
        namespace: Namespace = parser.parse_args(args)  # , NestedNameSpace())
        # check access to path.like attributes on the Namespace
        t.assertEqual(getattr(namespace, 'root.alpha'), 'value_a')
        t.assertEqual(getattr(namespace, 'root.command1.opt'), 'co1')

        # Create a Configuration Source from an argparse Namespace
        src = NamespaceConfig(namespace)
        t.assertEqual(src.get('root.alpha'), 'value_a')
        t.assertEqual(src.get('root.command1.opt'), 'co1')
        t.assertIsNone(src.get('root.command2.opt'))

        # Example using command2
        args = ['command2', '--cmd-option=co2']
        parser = argparser()
        namespace = parser.parse_args(args)
        src = NamespaceConfig(namespace)
        t.assertIsNone(src.get('root.command1.opt'))
        t.assertEqual(src.get('root.command2.opt'), 'co2')
