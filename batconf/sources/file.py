import logging as log

import os
from pathlib import Path
from typing import Union, List
from warnings import warn

from ..source import SourceInterface, OpStr
from .yaml import _load_yaml_file


_DEPRECATION_WARNING = (
    'FileConfig is deprecated and will be removed a future release.'
    ' FileConfig will be replaced with format-specific file sources.'
    ' batconf.sources.yaml.YamlConfig should be a direct replacement.'
)


class FileConfig(SourceInterface):

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
