from typing import Protocol, Literal, Any
from logging import getLogger

from pathlib import Path


log = getLogger(__name__)


# === Type Annotation and Protocols === #


class FileLoaderP(Protocol):
    def __call__(self, file_path: Path) -> Any: ...


ConfigFileFormats = Literal['flat', 'sections', 'environments']
_MissingFileOption = Literal['ignore', 'warn', 'error']
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
