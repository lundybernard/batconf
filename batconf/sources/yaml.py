# Postpones evaluation of type hints for compatibility
from __future__ import annotations
from typing import Any

import logging as log

from pathlib import Path

from .file import file_config_repr
from .types import MissingFileOption as _MissingFileOption
from ..source import SourceInterface


class YamlConfig(SourceInterface):
    """
    Configuration source backed by a YAML file.

    By default, the YAML file is interpreted as an environment-based
    configuration, where top-level keys define environments and
    ``config_env`` selects the active one.

    Parameters
    ----------
    config_file_name : str
        Path to the YAML configuration file.
    config_env : str or None, default=None
        Name of the active configuration environment. When
        ``config_env`` is not provided, the ``default`` environment
        defined in the YAML file is used.
    enable_config_environments : bool, default=True
        Whether the YAML file should be interpreted as an
        environment-based configuration.
    missing_file_option : {'warn', 'ignore', 'error'}, default='warn'
        Behavior when the specified config file is missing.

    Notes
    -----
    When environment-based configuration is enabled, the YAML file is
    expected to contain a top-level ``default`` key identifying the
    default environment, along with top-level mappings for each
    environment.
    """

    __data: Any

    def __init__(
        self,
        config_file_name: str,
        config_env: str | None = None,
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

    @property
    def _file_format(self) -> str:
        if self._enable_config_environments:
            return 'environments'
        return 'sections'

    def __getitem__(self, key: str) -> SourceInterface | str:
        path = key.split('.')
        conf = self._data
        for k in path:
            conf = conf[k]
        return conf

    def __str__(self) -> str:
        return f'Yaml File: {repr(self)}'

    __repr__ = file_config_repr

    def keys(self) -> list[str]:
        return self._data.keys()

    def get(self, key: str, module: str | None = None) -> str | None:
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
