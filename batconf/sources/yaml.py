# Postpones evaluation of type hints for compatibility
from __future__ import annotations

import logging as log

import yaml
from pathlib import Path
from typing import Union, List, Literal

from ..source import SourceInterface, OpStr


_MissingFileOption = Literal['ignore', 'warn', 'error']
_NestedDict = dict[str, Union[str, '_NestedDict']]


class YamlConfig(SourceInterface):
    __data: _NestedDict

    def __init__(
        self,
        config_file_name: str,
        config_env: OpStr = None,
        enable_config_environments: bool = True,
        missing_file_option: _MissingFileOption = 'warn',
    ):
        self._missing_file_option = missing_file_option
        self._config_file_path = get_file_path(
            file_name=config_file_name,
            when_missing=missing_file_option,
        )
        self._config_env = config_env
        self._enable_config_environments = enable_config_environments

        match missing_file_option:
            case 'ignore':
                self._data = _load_yaml_files_ignore_missing(
                    file_path=self._config_file_path,
                )
            case 'warn':
                self._data = _load_yaml_file_warn_on_mising(
                    file_path=self._config_file_path,
                )
            case 'error':
                self._data = _load_yaml_file(
                    file_path=self._config_file_path,
                )

    @property
    def _data(self) -> dict:
        return self.__data

    @_data.setter
    def _data(self, config: dict):
        if self._enable_config_environments:
            if not self._config_env:
                self._config_env = config['default']
            self.__data = config[self._config_env]
        else:
            self.__data = config

    def __getitem__(self, key: str) -> Union[SourceInterface, str]:
        print(f'YamlConfig.__getitem__({key})')
        path = key.split('.')
        conf = self._data
        for k in path:
            conf = conf[k]
        return conf

    def keys(self) -> List[str]:
        return self._data.keys()

    def get(self, key: str, module: OpStr = None) -> OpStr:
        if module:
            path = module.split('.') + key.split('.')
        else:
            path = key.split('.')

        conf = self._data
        for k in path:
            if not (conf := conf.get(k)):
                return conf
        return conf


_missing_config_warning = "Config File not found"


# === OS File Checker === #

def get_file_path(
    file_name: str,
    when_missing: _MissingFileOption = 'warn'
) -> Path:
    path = Path(file_name)

    print(f'{path=}')
    print(f'{path.is_file()=}')
    if path.is_file():
        return path

    relpath = path.resolve()
    print(f'{relpath=}, {relpath.is_file()=}')
    if relpath.is_file():
        print(f'set config_file_path to {relpath}')
        return relpath

    print(f'missing file {path}')
    match when_missing:
        case 'warn':
            log.warning(_missing_config_warning)
        case 'error':
            raise FileNotFoundError(
                f"Could not find Yaml Config file"
                f" Using absolute path: {path}"
                f" or relative path: {relpath}."
            )

    print('ignored missing file')
    return path

# === Yaml File Loader === #

def _load_yaml_file_warn_on_mising(file_path: Path) -> dict:
    try:
        config = _load_yaml_file(file_path)
    except FileNotFoundError:
        log.warning(_missing_config_warning)
        return {'default': 'none', 'none': {}}

    return config


def _load_yaml_files_ignore_missing(file_path) -> dict:
    try:
        config = _load_yaml_file(file_path)
    except FileNotFoundError:
        return {'default': 'none', 'none': {}}

    return config


def _load_yaml_file(file_path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required to use YamlConfig. "
            "Please install it using `pip install pyyaml`."
            "Or as an optional extra using `pip install batconf[yaml]`."
        )

    with open(file_path) as env_file:
        return yaml.load(env_file, Loader=yaml.BaseLoader)
