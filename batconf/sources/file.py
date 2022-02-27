import logging as log

import os
import yaml
from pathlib import Path
from typing import Union

from ..source import SourceInterface, Ostr


class FileConfig(SourceInterface):

    def __init__(
        self, config_file_name: Ostr = None, config_env: Ostr = None
    ) -> None:
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

    def keys(self) -> list[str]:
        return self._data.keys()

    def get(self, key: str, module: Ostr = None) -> Ostr:
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
    elif conf_path := os.environ.get(
        'BAT_CONFIG_FILE', default=None  # type: ignore
    ):
        pass
    elif (_conf_path := Path(os.getcwd() + '/config.yaml')).is_file():
        conf_path = _conf_path  # dont leave a dirty conf_path variable
    else:
        log.warn(_missing_config_warning)
        return {'default': 'none', 'none': 'empty'}

    with open(conf_path) as env_file:
        conf = yaml.load(env_file, Loader=yaml.BaseLoader)

    return conf


_missing_config_warning = (
    "Config File not specified:"
    " create config.yaml,"
    " set environment variable BAT_CONFIG_FILE to config file path,"
    " or speicfy a config file."
)
