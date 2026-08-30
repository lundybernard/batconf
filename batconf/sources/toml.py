from functools import cached_property
from typing import Any, cast
from logging import getLogger

from pathlib import Path

from .file import (
    _MissingFileOption,
    missing_file_handlers as _missing_file_handlers,
    file_config_repr,
)
from .types import ConfigFileFormats, FileSourceP


_OptStr = str | None
TomlDictT = dict[str, Any]

log = getLogger(__name__)


class TomlSource(FileSourceP):
    """Configuration source backed by a TOML file.

    Parameters
    ----------
    file_path : str
        Path to the TOML configuration file.
    file_format : {'environments', 'sections', 'flat'}, default='environments'
        TOML file layout. ``'environments'`` expects a ``[batconf]`` table
        with a ``default_env`` key and per-environment top-level tables;
        ``'sections'`` uses tables as config namespaces; ``'flat'`` reads
        all keys from the top-level table.
    config_env : str or None, default=read from file
        Active configuration environment. When not provided, the value of
        ``batconf.default_env`` in the TOML file is used.
    missing_file_option : {'warn', 'ignore', 'error'}, default='warn'
        Behaviour when the specified file is missing.

    Examples
    --------
    >>> src = TomlSource(file_path='config.toml', config_env='dev')
    """

    __config_env: str | None

    def __init__(
        self,
        file_path: str,
        file_format: ConfigFileFormats = 'environments',
        config_env: _OptStr = None,
        missing_file_option: _MissingFileOption = 'warn',
    ):
        self._config_file_path = Path(file_path)
        self._file_format = file_format
        self._config_env = config_env
        self._missing_file_option = missing_file_option

    def get(self, key: str, path: _OptStr = None) -> _OptStr:
        parts = path.split('.') + key.split('.') if path else key.split('.')
        conf: Any = self._data
        try:
            for k in parts:
                conf = conf.get(k)
        except AttributeError:
            return None
        return None if isinstance(conf, dict) else conf

    def keys(self) -> list[str]:
        return list(self._data.keys())

    @cached_property
    def _raw_data(self) -> TomlDictT:
        return _load_toml(
            file_path=self._config_file_path,
            when_missing=self._missing_file_option,
        )

    @cached_property
    def _data(self) -> TomlDictT:
        if self._raw_data is EmptyConfigDict:
            return self._raw_data

        if self._file_format == 'environments':
            try:
                # the environments format always resolves a _config_env
                return self._raw_data[cast(str, self._config_env)]
            except KeyError as err:
                raise ValueError(
                    f'Config Environment "{self._config_env}" '
                    f'not found in {self._config_file_path}'
                ) from err

        return self._raw_data

    @property
    def _config_env(self) -> str | None:
        if self._file_format != 'environments':
            return None
        if self.__config_env is None:
            if self._raw_data is not EmptyConfigDict:
                self.__config_env = self._raw_data['batconf']['default_env']
        return self.__config_env

    @_config_env.setter
    def _config_env(self, env: str | None) -> None:
        if not self._file_format == 'environments':
            self.__config_env = None
            return
        else:
            self.__config_env = env

    def __str__(self):
        return f'Toml File: {repr(self)}'

    __repr__ = file_config_repr


EmptyConfigDict: dict[None, None] = dict()


# === TOML File Loader Functions === #


def _load_toml(
    file_path: Path,
    when_missing: _MissingFileOption = 'warn',
) -> TomlDictT:
    return _missing_file_handlers[when_missing](
        loader_fn=_load_toml_file,
        file_path=file_path,
        empty_fallback=EmptyConfigDict,
    )


def _load_toml_file(file_path: Path) -> TomlDictT:
    load = _import_toml_load_function()

    # TODO: switch to binary format after 3.10 support is dropped
    # with open(file_path, 'rb') as cfg_file:
    with open(file_path, 'r') as cfg_file:
        config = load(cfg_file.read())

    return config


def _import_toml_load_function():
    try:
        from tomllib import loads  # type: ignore[import-not-found]
    except ImportError:
        log.debug('failed to import tomllib.load, is python < v3.11')
        try:
            from toml import loads  # type: ignore[assignment]
        except ImportError as e:
            raise ImportError(_TOML_IMPORT_ERROR_MSG) from e

    return loads


_TOML_IMPORT_ERROR_MSG = (
    'Failed to import toml.load,'
    ' for python < 3.11, the toml package is required.'
    ' Install the optional extra batconf[toml]'
)
