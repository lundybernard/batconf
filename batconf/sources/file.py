from typing import Union, List, Protocol, Literal, Any
import logging as log

import os

from pathlib import Path
from warnings import warn

from ..source import SourceInterface, OpStr
from .yaml import _load_yaml_file


class FileLoaderP(Protocol):
    def __call__(self, path: Path) -> Any: ...


_MissingFileOption = Literal['ignore', 'warn', 'error']


def load_file_warn_when_mising(
    loader_fn: FileLoaderP,
    file_path: Path,
) -> dict:
    try:
        config = loader_fn(file_path)
    except FileNotFoundError:
        log.warning(_missing_config_warning)
        return {'default': 'none', 'none': {}}

    return config


def load_file_ignore_when_missing(
    loader_fn: FileLoaderP,
    file_path: Path,
) -> dict:
    try:
        config = loader_fn(file_path)
    except FileNotFoundError:
        return {'default': 'none', 'none': {}}

    return config


def get_file_path(
    file_name: str,
    when_missing: _MissingFileOption = 'warn'
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
            f"Could not find Yaml Config file"
            f" Using absolute path: {path}"
            f" or relative path: {relpath}."
        )

    return path


# === Deprecated FileConfig class === #


_DEPRECATION_WARNING = (
    'FileConfig is deprecated and will be removed a future release.'
    ' FileConfig will be replaced with format-specific file sources.'
    ' batconf.sources.yaml.YamlConfig should be a direct replacement.'
)


class FileConfig(SourceInterface):
    """
    .. deprecated:: 0.2.0
       Use a file-type specific loader instead.
       Such as `batconf.sources.yaml.YamlConfig`.
    """


    def __init__(
        self, config_file_name: OpStr = None, config_env: OpStr = None
    ) -> None:
        warn(_DEPRECATION_WARNING)

        config = load_config_file(config_file_name)

        if not config_env:
            config_env = config['default']

        self._data = config[config_env]

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



def load_config_file(config_file: Union[Path, str, None] = None) -> dict:
    """
        .. deprecated:: 2.0
           Use `new_function` instead.
        """

    if conf_path := config_file:
        pass
    elif conf_path := os.environ.get('BAT_CONFIG_FILE', default=None):
        pass
    elif (_conf_path := Path(os.getcwd() + '/config.yaml')).is_file():
        conf_path = _conf_path  # dont leave a dirty conf_path variable
    else:
        log.warning(_missing_config_warning)
        return {'default': 'none', 'none': {}}

    conf = _load_yaml_file(file_path=Path(conf_path))

    return conf


_missing_config_warning = (
    "Config File not specified:"
    " create config.yaml,"
    " set environment variable BAT_CONFIG_FILE to config file path,"
    " or speicfy a config file."
)
