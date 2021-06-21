from unittest import TestCase

from ..args import CliArgsConfig, Namespace


class TestCliArgsConfig(TestCase):
    '''For now Argparse Namespace objects are not nested
    all args are top-level properties.
    This should be changed in the future
    to avoid overriding default values in one module
    with cli args intended for another
    '''

    def test_get(t):
        cli_args = Namespace(
            config_file='example.config.yaml',
            key='value'
        )

        conf = CliArgsConfig(cli_args)

        with t.subTest('single key'):
            t.assertEqual(conf.get('config_file'), 'example.config.yaml')

        with t.subTest('missing value'):
            t.assertEqual(conf.get('missing'), None)

        with t.subTest('module value'):
            t.assertEqual(conf.get('key', module='bat.module'), 'value')

        with t.subTest('module and key paths'):
            t.assertEqual(
                conf.get('to.key', module='bat.module.path'),
                'value'
            )
