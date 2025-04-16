# Postpones evaluation of type hints for compatibility
from __future__ import annotations
from typing import Any

import logging as log

from pathlib import Path
from typing import Union, List, Literal

from ..source import SourceInterface, OpStr


_MissingFileOption = Literal['ignore', 'warn', 'error']


class YamlConfig(SourceInterface):
    __data: Any

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

        self._data = _load_yaml(
            file_path=self._config_file_path,
            when_missing=self._missing_file_option,
        )

    @property
    def _data(self) -> Any:
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


_missing_config_warning = 'Config File not found'


# === OS File Checker === #


def get_file_path(
    file_name: str, when_missing: _MissingFileOption = 'warn'
) -> Path:
    path = Path(file_name)

    if path.is_file():
        return path

    relpath = path.resolve()
    if relpath.is_file():
        return relpath

    if when_missing == 'warn':
        log.warning(_missing_config_warning)
    elif when_missing == 'error':
        raise FileNotFoundError(
            f'Could not find Yaml Config file'
            f' Using absolute path: {path}'
            f' or relative path: {relpath}.'
        )

    return path


# === Yaml File Loader === #


def _load_yaml(
    file_path: Path,
    when_missing: _MissingFileOption,
) -> dict:
    # TODO: Replace with a match statement when support for py3.9 is dropped
    loader_map = {
        'ignore': _load_yaml_file_ignore_when_missing,
        'warn': _load_yaml_file_warn_when_missing,
        'error': _load_yaml_file,
    }
    return loader_map[when_missing](file_path=file_path)


def _load_yaml_file_warn_when_missing(file_path: Path) -> dict:
    try:
        config = _load_yaml_file(file_path)
    except FileNotFoundError:
        log.warning(_missing_config_warning)
        return {'default': 'none', 'none': {}}

    return config


def _load_yaml_file_ignore_when_missing(file_path: Path) -> dict:
    try:
        config = _load_yaml_file(file_path)
    except FileNotFoundError:
        return {'default': 'none', 'none': {}}

    return config


def _load_yaml_file(file_path: Path) -> dict:
    try:
        import yaml
    except ImportError as e:
        raise ImportError(_YAML_IMPORT_ERROR_MSG) from e

    with open(file_path) as env_file:
        return yaml.load(env_file, Loader=yaml.BaseLoader)


_YAML_IMPORT_ERROR_MSG = (
    'PyYAML is required to use YamlConfig. '
    'Please install it using `pip install pyyaml`.'
    'Or as an optional extra using `pip install batconf[yaml]`.'
)
