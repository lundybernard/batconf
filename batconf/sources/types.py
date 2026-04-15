from typing import Literal, Protocol

ConfigFileFormats = Literal['flat', 'sections', 'environments']
MissingFileOption = Literal['ignore', 'warn', 'error']


class SourceInterfaceProto(Protocol):
    def get(self, key: str, path: str | None) -> str | None: ...


class FileSourceP(SourceInterfaceProto, Protocol):
    """Protocol for file-backed configuration sources.

    Defines the standard constructor and query interface that all
    file-based configuration sources must satisfy.

    Parameters
    ----------
    file_path : str
        Path to the configuration file.
    file_format : {'environments', 'sections', 'flat'}, default='environments'
        File layout. ``'environments'`` reads a per-environment subtree
        selected by ``config_env``; ``'sections'`` uses top-level sections
        as namespaces; ``'flat'`` reads from a single top-level mapping.
    config_env : str or None, default=None
        Active configuration environment. When ``None``, the default
        defined inside the file is used.
    missing_file_option : {'warn', 'ignore', 'error'}, default='warn'
        Behaviour when the specified file does not exist.
    """

    def __init__(
        self,
        file_path: str,
        file_format: ConfigFileFormats = 'environments',
        config_env: str | None = None,
        missing_file_option: MissingFileOption = 'warn',
    ) -> None: ...


__all__ = [
    'ConfigFileFormats',
    'FileSourceP',
    'MissingFileOption',
    'SourceInterfaceProto',
]
