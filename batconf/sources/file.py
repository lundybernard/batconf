from typing import Protocol, Any
from logging import getLogger

from pathlib import Path

from ..errors import ConfigFileNotFound
from .types import MissingFileOption


log = getLogger(__name__)


# === Type Annotation and Protocols === #


class FileLoaderP(Protocol):
    def __call__(self, file_path: Path) -> Any: ...


class MissingFileHandlerP(Protocol):
    def __call__(
        self,
        loader_fn: FileLoaderP,
        file_path: Path,
        empty_fallback: Any,
    ) -> Any: ...


def load_file_warn_when_missing(
    loader_fn: FileLoaderP,
    file_path: Path,
    empty_fallback: Any,
) -> Any:
    try:
        config = loader_fn(file_path)
    except FileNotFoundError:
        log.warning(f'Config file not found: {file_path}')
        return empty_fallback

    return config


def load_file_ignore_when_missing(
    loader_fn: FileLoaderP,
    file_path: Path,
    empty_fallback: Any,
) -> Any:
    try:
        config = loader_fn(file_path)
    except FileNotFoundError:
        return empty_fallback

    return config


def load_file_error_when_missing(
    loader_fn: FileLoaderP,
    file_path: Path,
    empty_fallback: Any = ...,
):
    return loader_fn(file_path)


def check_missing_file(
    file_path: Path,
    when_missing: MissingFileOption,
) -> None:
    """Report a missing config file before anything reads it.

    Raises
    ------
    ConfigFileNotFound
        ``when_missing`` is ``'error'`` and ``file_path`` does not exist.
    """
    if when_missing != 'error':
        return
    if not file_path.exists():
        raise ConfigFileNotFound(f'Config file not found: {file_path}')


missing_file_handlers: dict[str, MissingFileHandlerP] = {
    'warn': load_file_warn_when_missing,
    'ignore': load_file_ignore_when_missing,
    'error': load_file_error_when_missing,
}


class FileConfigReprP(Protocol):
    _config_file_path: Path | str | None
    _config_env: str | None
    _missing_file_option: str
    _file_format: str


def file_config_repr(self: FileConfigReprP) -> str:
    return (
        f'{self.__class__.__name__}('
        f'file_path={self._config_file_path}, '
        f'config_env={self._config_env}, '
        f'missing_file_option={self._missing_file_option}, '
        f'file_format={self._file_format}'
        ')'
    )
