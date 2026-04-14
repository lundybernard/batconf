from typing import Protocol, Any
from logging import getLogger

from pathlib import Path

from .types import ConfigFileFormats, MissingFileOption

# backwards-compatible internal alias
_MissingFileOption = MissingFileOption


log = getLogger(__name__)


# === Type Annotation and Protocols === #


class FileLoaderP(Protocol):
    def __call__(self, file_path: Path) -> Any: ...
EmptyConfigurationSentinel = object()


# EmptyConfiguration = {'default': 'none', 'none': {}}
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


missing_file_handlers: dict[str, MissingFileHandlerP] = {
    'warn': load_file_warn_when_missing,
    'ignore': load_file_ignore_when_missing,
    'error': load_file_error_when_missing,
}


class FileConfigReprProtocol(Protocol):
    _config_file_path: Path | str | None
    _config_env: str | None
    _missing_file_option: str
    _file_format: str


def file_config_repr(self: FileConfigReprProtocol) -> str:
    return (
        f'{self.__class__.__name__}('
        f'file_path={self._config_file_path}, '
        f'config_env={self._config_env}, '
        f'missing_file_option={self._missing_file_option}, '
        f'file_format={self._file_format}'
        ')'
    )
