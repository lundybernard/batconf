from typing import Any
from logging import getLogger

from pathlib import Path
from enum import Enum, auto

from .file import (
    ConfigFileFormats,
    _MissingFileOption,
    missing_file_handlers as _missing_file_handlers,
    file_config_repr,
)
from .types import FileSourceP


_OptStr = str | None
TomlDictT = dict[str, Any]

log = getLogger(__name__)


class _DEFAULTS(Enum):
    environment = auto()


class TomlConfig(FileSourceP):
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

        self._data = _load_toml(
            file_path=self._config_file_path,
            when_missing=self._missing_file_option,
        )

    def get(self, key: str, path: _OptStr = None) -> _OptStr:
        if path:
            pth = path.split('.') + key.split('.')
        else:
            pth = key.split('.')

        conf = self._data
        for k in pth:
            if not (conf := conf.get(k)):
                return conf

        return conf if type(conf) is not dict else None

    def keys(self) -> list[str]:
        return self._data.keys()

    @property
    def _data(self):
        return self.__data

    @_data.setter
    def _data(self, config: dict):
        if config is EmptyConfigDict:
            self.__data = config
            return

        if self._file_format == 'environments':
            if not self._config_env:
                self._config_env = config['batconf']['default_env']
            # Load only the specified config_env from the config dict
            try:
                self.__data = config[self._config_env]
            except KeyError as err:
                raise ValueError(
                    f'Config Environment "{self._config_env}" '
                    f'not found in {self._config_file_path}'
                ) from err

        else:
            self.__data = config

    # TODO: Fix type-hints when the next version of MyPy is released
    @property
    def _config_env(self):  # -> str:
        return self.__config_env

    @_config_env.setter
    def _config_env(self, env):  # _EnvOpts):
        if not self._file_format == 'environments':
            self.__config_env = None  # type: ignore[assignment]
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
        from tomllib import loads  # type: ignore  # noqa
    except ImportError:
        log.debug('failed to import tomllib.load, is python < v3.11')
        try:
            from toml import loads  # type: ignore  # noqa
        except ImportError as e:
            raise ImportError(_TOML_IMPORT_ERROR_MSG) from e

    return loads


_TOML_IMPORT_ERROR_MSG = (
    'Failed to import toml.load,'
    ' for python < 3.11, the toml package is required.'
    ' install the optional extra batconf[toml]'
)
