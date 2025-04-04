from typing import Literal, Protocol, Callable, Optional, Union
from logging import getLogger

from configparser import ConfigParser
from pathlib import Path
from enum import Enum, auto

from ..source import SourceInterface

from .file import (
    ConfigFileFormats,
    _MissingFileOption,
    load_file_warn_when_missing,
    load_file_ignore_when_missing,
    load_file_error_when_missing,
    FileLoaderP,
    MissingFileHandlerP,
)


log = getLogger(__name__)


_OptStr = Optional[str]


class _DEFAULTS(Enum):
    environment = auto()


_EnvOpts = Union[str, Literal[_DEFAULTS.environment], None]


class ConfigParserP(Protocol):
    def get(
        self,
        section: str,
        option: str,
        fallback: _OptStr = None,
    ) -> _OptStr: ...


# === IniConfig Get Methods === #


class _ConfigParserSource(Protocol):
    _config_env: _EnvOpts
    _data: ConfigParser


def _get_envs(
    self: _ConfigParserSource,
    key: str,
    path: _OptStr = None,
) -> _OptStr:
    if path:
        key = f'{path}.{key}'

    try:
        section, key = key.rsplit(sep='.', maxsplit=1)
    except ValueError:
        # Type checking should be fixed in the next MyPy release
        section = self._config_env  # type: ignore[assignment]
    else:
        section = f'{self._config_env}.{section}'

    return self._data.get(
        option=key,
        section=section,
        fallback=None,
    )


def _get_sections(
    self: _ConfigParserSource,
    key: str,
    path: _OptStr = None,
) -> _OptStr:
    if path:
        key = f'{path}.{key}'

    try:
        section, key = key.rsplit(sep='.', maxsplit=1)
    except ValueError:
        section = ''

    return self._data.get(section=section, option=key, fallback=None)


def _get_flat(
    self: _ConfigParserSource,
    key: str,
    path: _OptStr = None,
) -> _OptStr:
    return self._data.get(section='root', option=key, fallback=None)


def _get_empty(
    self: _ConfigParserSource,
    key: str,
    path: _OptStr = None,
) -> _OptStr:
    return None


_getter_methods = {
    'environments': _get_envs,
    'sections': _get_sections,
    'flat': _get_flat,
    'empty': _get_empty,
}


class EmptyConfigParser:
    def get(self, section: str, option: str, fallback=None) -> None: ...


# === IniConfig Class === #


class IniConfig(SourceInterface):
    _data: Union[ConfigParser, EmptyConfigParser] = EmptyConfigParser()
    _get_impl: Callable
    __config_env: str

    def __init__(
        self,
        file_path: str,
        config_env: _EnvOpts = _DEFAULTS.environment,
        missing_file_option: _MissingFileOption = 'warn',
        file_format: ConfigFileFormats = 'environments',
    ):
        self._missing_file_option = missing_file_option
        self._file_format = file_format
        self._config_file_path = Path(file_path)

        self._data = _load_ini(
            file_path=self._config_file_path,
            file_format=self._file_format,
            when_missing=self._missing_file_option,
        )

        self._config_env = config_env  # type: ignore[assignment]
        # This mypy error will be fixed by
        # https://github.com/python/mypy/pull/18510

        if self._data is EmptyConfigParser:
            self._get_impl = _getter_methods['empty']
        else:
            try:
                self._get_impl = _getter_methods[file_format]
            except KeyError:
                raise ValueError(f'Invalid file_format: {file_format}')

    def get(self, key: str, path: _OptStr = None) -> _OptStr:
        # TODO: fully deprecate the path parameter
        return self._get_impl(self, key=key, path=path)

    # TODO: Fix type-hints when the next version of MyPy is released
    @property
    def _config_env(self):  # -> str:
        return self.__config_env

    @_config_env.setter
    def _config_env(self, env):  # _EnvOpts):
        if (
            self._file_format != 'environments'
            or self._data is EmptyConfigParser
        ):
            self.__config_env = None  # type: ignore[assignment]
            return

        if env is _DEFAULTS.environment or env is None:
            # use the batconf.default_env value from the config file
            self.__config_env = self._data.get('batconf', 'default_env')
        else:
            self.__config_env = env

        if not self._data.has_section(self._config_env):
            raise ValueError(
                f'Config Environment "{self._config_env}" '
                f'not found in {self._config_file_path}'
            )


# === INI File Loader Functions === #


def _load_ini(
    file_path: Path,
    file_format: ConfigFileFormats,
    when_missing: _MissingFileOption = 'warn',
) -> Union[ConfigParser, EmptyConfigParser]:
    loader_fn = _file_type_loaders[file_format]
    return _missing_file_handlers[when_missing](
        loader_fn=loader_fn,
        file_path=file_path,
        empty_fallback=EmptyConfigParser,
    )


def _load_ini_file(file_path: Path) -> ConfigParser:
    config = ConfigParser()
    if not config.read(file_path):
        raise FileNotFoundError(f'Failed to load config file: {file_path}')

    return config


def _load_ini_file_flat(file_path: Path) -> ConfigParser:
    config = ConfigParser()
    with open(file_path) as cfg_file:
        config.read_string(f'[root]\n{cfg_file.read()}')

    return config


_file_type_loaders: dict[str, FileLoaderP] = {
    'environments': _load_ini_file,
    'sections': _load_ini_file,
    'flat': _load_ini_file_flat,
}


_missing_file_handlers: dict[str, MissingFileHandlerP] = {
    'warn': load_file_warn_when_missing,
    'ignore': load_file_ignore_when_missing,
    'error': load_file_error_when_missing,
}

_file_loader_map = {
    (ini_format, when_missing): (loader_fn, handler_fn)
    for ini_format, loader_fn in _file_type_loaders.items()
    for when_missing, handler_fn in _missing_file_handlers.items()
}


_MOD_PARAM_DEPRECATION_WARNING = (
    'The module argument is deprecated and will be removed'
    ' from the SourceInterface.get interface in a future release.'
)
