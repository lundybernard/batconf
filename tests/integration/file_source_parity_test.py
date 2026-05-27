from unittest import TestCase
from os import path

from batconf import IniSource, TomlSource, YamlSource
from batconf.types import FILE_FORMATS


_TOML_INSTALLED = True
try:
    import tomllib  # type: ignore[import-not-found]  # noqa: F401
except ImportError:
    try:
        import toml  # noqa: F401
    except ImportError:
        _TOML_INSTALLED = False

_PYYAML_INSTALLED = True
try:
    import yaml  # noqa: F401
except ImportError:
    _PYYAML_INSTALLED = False


_DATA_DIR = path.join(path.dirname(path.realpath(__file__)), 'data')

_SOURCE_EXT = {
    IniSource: 'ini',
    TomlSource: 'toml',
    YamlSource: 'yaml',
}

_FORMAT_PREFIX = {
    'environments': 'envs',
    'sections': 'sections',
    'flat': 'flat',
}

_ALL_SOURCES = [
    s
    for s in [
        IniSource,
        TomlSource if _TOML_INSTALLED else None,
        YamlSource if _PYYAML_INSTALLED else None,
    ]
    if s is not None
]


def _file_path(source_class, file_format):
    prefix = _FORMAT_PREFIX[file_format]
    ext = _SOURCE_EXT[source_class]
    return path.join(_DATA_DIR, f'{prefix}.config.{ext}')


class FileSourceSignatureParityTests(TestCase):
    """All file sources accept the same FileSourceP constructor arguments."""

    def test_all_sources_accept_FileSourceP_args(t):
        for file_format in FILE_FORMATS:
            for source_class in _ALL_SOURCES:
                with t.subTest(
                    source=source_class.__name__,
                    file_format=file_format,
                ):
                    src = source_class(
                        file_path='nonexistent.file',
                        file_format=file_format,
                        missing_file_option='ignore',
                    )
                    t.assertIsNotNone(src)

    def test_missing_key_returns_None_for_all_sources(t):
        for file_format in FILE_FORMATS:
            for source_class in _ALL_SOURCES:
                with t.subTest(
                    source=source_class.__name__, file_format=file_format
                ):
                    src = source_class(
                        file_path='nonexistent.file',
                        file_format=file_format,
                        missing_file_option='ignore',
                    )
                    t.assertIsNone(src.get('missing.key'))
                    t.assertIsNone(src.get('key', path='missing.path'))


class FileSourceValueParityTests(TestCase):
    """All file sources return equivalent values for the same logical key."""

    def setUp(t):
        t.env_sources = [
            t._load(cls, 'environments')
            for cls in _ALL_SOURCES
            if cls is not None
        ]

    def _load(t, source_class, file_format):
        return source_class(
            file_path=_file_path(source_class, file_format),
            file_format=file_format,
        )

    def test_environments_format_parity(t):
        sources = [
            t._load(cls, 'environments')
            for cls in _ALL_SOURCES
            if cls is not None
        ]
        for src in sources:
            with t.subTest(source=type(src).__name__):
                t.assertEqual(src.get('doc'), 'our testing environment')
                t.assertIsNotNone(src.get('project.submodule.sub.key1'))
                t.assertIsNone(src.get('missing_key'))
                t.assertIsNone(src.get('project.submodule'))

    def test_sections_format_parity(t):
        sources = [
            t._load(cls, 'sections')  # nofmt
            for cls in _ALL_SOURCES
            if cls is not None
        ]
        for src in sources:
            with t.subTest(source=type(src).__name__):
                t.assertIsNotNone(src.get('sec0.sub0.value0'))
                t.assertIsNone(src.get('missing_key'))
                t.assertIsNone(src.get('sec0'))

    def test_flat_format_parity(t):
        sources = [
            t._load(cls, 'flat')  # nofmt
            for cls in _ALL_SOURCES
            if cls is not None
        ]
        for src in sources:
            with t.subTest(source=type(src).__name__):
                t.assertEqual(src.get('int'), '0')
                t.assertEqual(src.get('root'), 'is a valid key')
                t.assertIsNone(src.get('missing_key'))

    def test_path_past_terminal_string_returns_None(t):
        """Traversing past a leaf string value returns None, not an error.

        Dict-traversal sources (TOML, YAML) also emit a WARNING.
        IniSource handles this natively via ConfigParser fallback — no warning.
        """
        cases = [
            ('environments', t.env_sources),
            ('sections', [t._load(cls, 'sections') for cls in _ALL_SOURCES]),
        ]
        keys = {
            'environments': ('nonexistent', 'project.submodule.sub.key1'),
            'sections': ('nonexistent', 'sec0.sub0.value0'),
        }
        for fmt, sources in cases:
            key, path = keys[fmt]
            for src in sources:
                with t.subTest(fmt=fmt, source=type(src).__name__):
                    if isinstance(src, IniSource):
                        t.assertIsNone(src.get(key, path=path))
                    else:
                        with t.assertLogs(type(src).__module__, level='WARNING') as cm:
                            result = src.get(key, path=path)
                        t.assertIsNone(result)
                        t.assertEqual(
                            cm.records[0].getMessage(),
                            f'Config path {path}.{key} does not exist',
                        )
