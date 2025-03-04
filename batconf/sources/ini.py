from typing import Callable, Literal
from logging import getLogger

from configparser import ConfigParser
from pathlib import Path
from functools import partial, cached_property

from ..source import SourceInterface, OpStr

from .file import (
    _MissingFileOption,
    get_file_path,
    load_file_warn_when_mising,
    load_file_ignore_when_missing,
)


log = getLogger(__name__)


IniConfigFileFormats = Literal['flat', 'sections', 'environments']


class IniConfig:
    '''A factory class that returns an instance of the appropriate configuration class
    when instantiated directly.
    '''
    def __new__(
        cls,
        file_path: str,
        config_env: OpStr = None,
        missing_file_option: _MissingFileOption = 'warn',
        file_format: IniConfigFileFormats = 'environments',
    ) -> SourceInterface:
        """
        Return an instance of IniConfigWithEnvironments or IniConfigFlat
        depending on the value of enable_config_environments.
        """
        if file_format == 'environments':
            return IniConfigEnvs(
                file_path=file_path,
                config_env=config_env,
                missing_file_option=missing_file_option,
            )
        if file_format == 'sections':
            return IniConfigSect(
                file_path=file_path,
                missing_file_option=missing_file_option,
            )
        if file_format == 'flat':
            return IniConfigFlat(
                file_path=file_path,
                missing_file_option=missing_file_option,
            )


class IniConfigEnvs(SourceInterface):
    def __init__(
        self,
        file_path: str,
        config_env: OpStr = None,
        missing_file_option: _MissingFileOption = 'warn',
    ):
        self._missing_file_option = missing_file_option
        self._config_file_path = get_file_path(
            file_name=file_path,
            when_missing=missing_file_option,
        )
        self._data = _load_ini_file(self._config_file_path)
        self._config_env = config_env

    def get(
        self,
        key: str,
        module: str | None = None
    ) -> str | None:
        # TODO: fully deprecate the module parameter and remove this check
        if module:
            raise NotImplementedError(''
                'The module argument is deprecated and will be removed'
                ' from the SourceInterface.get interface in a future release.'
            )

        print(f'get({key=})')
        try:
            section, key = key.rsplit(sep='.', maxsplit=1)
        except ValueError:
            val = self._data.get(
                option=key,
                section=self._config_env,
                fallback=None,
            )
        else:
            val = self._data.get(
                option=key,
                section=f'{self._config_env}.{section}',
                fallback=None,
            )
        return val

    @property
    def _config_env(self) -> str:
        return self.__config_env

    @_config_env.setter
    def _config_env(self, env: str):
        if env:
            self.__config_env = env
        else:
            self._config_env = self._data.get('batconf', 'default_env')

        if not self._data.has_section(self._config_env):
            raise ValueError(
                f'Config Environment "{self._config_env}" '
                f'not found in {self._config_file_path}'
            )


class IniConfigSect(SourceInterface):
    pass


class IniConfigFlat(SourceInterface):
    pass


def _load_ini(
    file_path: Path,
    when_missing: _MissingFileOption = 'warn',
) -> ConfigParser:
    # TODO: Replace with a match statement when support for py3.9 is dropped
    loader_map: dict[str, Callable] = {
        'ignore': partial(
            load_file_ignore_when_missing,
            loader_fn=_load_ini_file,
        ),
        'warn': partial(
            load_file_warn_when_mising,
            loader_fn=_load_ini_file,
        ),
        'error': _load_ini_file,
    }
    return loader_map[when_missing](file_path=file_path)


def _load_ini_file(file_path: Path) -> ConfigParser:
    config = ConfigParser()
    if not config.read(file_path):
        raise FileNotFoundError(f'Failed to load config file: {file_path}')

    return config
