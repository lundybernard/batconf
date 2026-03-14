from unittest import TestCase
from unittest.mock import patch, create_autospec, sentinel


from ..file import (
    # missing file handlers
    MissingFileHandlerP,
    load_file_warn_when_missing,
    load_file_ignore_when_missing,
    load_file_error_when_missing,
    Path,
)


SRC = 'batconf.sources.file'


EXAMPLE_CONFIG_YAML = """
default: example

example:
    bat:
        key: value
        remote_host:
            api_key: example_api_key
            url: https://api-example.host.io/

alt:
    bat:
        module:
            key: alt_value
"""


EXAMPLE_CONFIG_DICT: dict = {
    'default': 'example',
    'example': {
        'bat': {
            'key': 'value',
            'remote_host': {
                'api_key': 'example_api_key',
                'url': 'https://api-example.host.io/',
            },
        },
    },
    'alt': {'bat': {'module': {'key': 'alt_value'}}},
}


class FileLoaderFunctionTests(TestCase):
    def setUp(t):
        t.loader_fn = create_autospec(MissingFileHandlerP, spec_set=True)
        t.file_name = 'example.config.file'
        t.file_path = Path(t.file_name)

    def test_load_file_warn_when_missing(t):
        with t.subTest('file_path exists'):
            ret = load_file_warn_when_missing(
                loader_fn=t.loader_fn,
                file_path=t.file_path,
                empty_fallback=sentinel.EmptyConfig,
            )
            t.assertIs(t.loader_fn.return_value, ret)

        with t.subTest('file_path does not exist'):
            t.loader_fn.side_effect = FileNotFoundError

            with patch(f'{SRC}.log', autospec=True) as log:
                ret = load_file_warn_when_missing(
                    loader_fn=t.loader_fn,
                    file_path=t.file_path,
                    empty_fallback=sentinel.EmptyConfig,
                )
                log.warning.assert_called_with(
                    f'Config file not found: {t.file_name}',
                )
                t.assertEqual(ret, sentinel.EmptyConfig)
                t.loader_fn.assert_called_with(t.file_path)

    def test_load_file_ignore_when_missing(t):
        with t.subTest('file_path exists'):
            ret = load_file_ignore_when_missing(
                loader_fn=t.loader_fn,
                file_path=t.file_path,
                empty_fallback=sentinel.EmptyConfig,
            )
            t.assertIs(t.loader_fn.return_value, ret)

        with t.subTest('file_path does not exist'):
            t.loader_fn.side_effect = FileNotFoundError
            ret = load_file_ignore_when_missing(
                loader_fn=t.loader_fn,
                file_path=t.file_path,
                empty_fallback=sentinel.EmptyConfig,
            )
            t.assertEqual(ret, sentinel.EmptyConfig)
            t.loader_fn.assert_called_with(t.file_path)

    def test_load_file_error_when_missing(t):
        with t.subTest('file_path exists'):
            ret = load_file_error_when_missing(
                loader_fn=t.loader_fn,
                file_path=t.file_path,
            )
            t.assertIs(t.loader_fn.return_value, ret)

        with t.subTest('file_path does not exist'):
            t.loader_fn.side_effect = FileNotFoundError

            with t.assertRaises(FileNotFoundError):
                _ = load_file_error_when_missing(
                    loader_fn=t.loader_fn,
                    file_path=t.file_path,
                )
