from unittest import TestCase, skipIf
from unittest.mock import patch, Mock

from os import path

from batconf.sources.yaml import YamlSource
from batconf.types import FILE_FORMATS


_PYYAML_INSTALLED = True
try:
    import yaml  # noqa: F401
except ImportError:
    _PYYAML_INSTALLED = False


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class YamlSourceIntegrationTests(TestCase):
    def setUp(t):
        t.this_dir = path.dirname(path.realpath(__file__))

    def test_yaml_file_source_defaults(t):
        t.config_file_path = path.join(t.this_dir, 'data/envs.config.yaml')
        ys = YamlSource(file_path=t.config_file_path)

        t.assertEqual('our testing environment', ys.get('doc'))
        t.assertEqual(
            'envs.config.yaml: test.project.submodule.sub.key1',
            ys.get('project.submodule.sub.key1'),
        )
        t.assertIsNone(ys.get('project.submodule'))

    def test_section_file(t):
        t.config_file_path = path.join(t.this_dir, 'data/sections.config.yaml')
        ys = YamlSource(file_path=t.config_file_path, file_format='sections')

        t.assertEqual(
            'sections.config.yaml :: sec0.sub0 :: value0',
            ys.get('sec0.sub0.value0'),
        )
        t.assertIsNone(ys.get('sec0'))
        t.assertIsNone(ys.get('sec0.sub0'))

    def test_flat_file(t):
        t.config_file_path = path.join(t.this_dir, 'data/flat.config.yaml')
        ys = YamlSource(file_path=t.config_file_path, file_format='flat')

        t.assertEqual('value 0', ys.get('value0'))
        t.assertEqual('0', ys.get('int'))
        t.assertIsNone(ys.get('undefined-key'))
        t.assertEqual('is a valid key', ys.get('root'))

    def test_config_env_argument(t):
        t.config_file_path = path.join(t.this_dir, 'data/envs.config.yaml')
        ys = YamlSource(file_path=t.config_file_path, config_env='production')
        t.assertEqual('Options for the production environment', ys.get('doc'))


@skipIf(not _PYYAML_INSTALLED, 'optional pyyaml module not installed')
class YamlSourceMissingFileTests(TestCase):
    def setUp(t):
        t.filename = 'sir.not.appearing.in.this.film'

    @patch('batconf.sources.file.log', autospec=True)
    def test_warning_default(t, log: Mock):
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                ys = YamlSource(
                    file_path=t.filename,
                    file_format=file_format,
                )
                # lazy: warning emitted on first data access, not construction
                t.assertIsNone(ys.get('root'))
                log.warning.assert_called_with(
                    f'Config file not found: {t.filename}'
                )
            t.assertIsNone(ys.get('project.submodule.sub.key1'))
            t.assertIsNone(ys.get('any.random.key'))

    def test_missing_file_error(t):
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                ys = YamlSource(
                    file_path=t.filename,
                    missing_file_option='error',
                    file_format=file_format,
                )
                # lazy: error raised on first data access, not construction
                with t.assertRaises(FileNotFoundError):
                    ys.get('root')

    def test_missing_file_ignore(t):
        for file_format in FILE_FORMATS:
            with t.subTest(file_format=file_format):
                ys = YamlSource(
                    file_path=t.filename,
                    missing_file_option='ignore',
                    file_format=file_format,
                )
                t.assertIsNone(ys.get('doc'))
                t.assertIsNone(ys.get('project.submodule.sub.key1'))
                t.assertIsNone(ys.get('any.random.key'))
