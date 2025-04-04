from typing import Union, List, Protocol, Literal, Any
from logging import getLogger

import os

from pathlib import Path
from warnings import warn

from ..source import SourceInterface, OpStr
from .yaml import _load_yaml_file


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
    'Config File not specified:'
    ' create config.yaml,'
    ' set environment variable BAT_CONFIG_FILE to config file path,'
    ' or speicfy a config file.'
)
