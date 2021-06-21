import logging as log

import os
import yaml
from pathlib import Path

from ..source import SourceInterface


class FileConfig(SourceInterface):

    def __init__(self, config_file_name=None, config_env=None):
        config = load_config_file(config_file_name)

        if not config_env:
            config_env = config['default']

        self._data = config[config_env]

    def __getitem__(self, key):
        path = key.split('.')
        conf = self._data
        for k in path:
            conf = conf[k]
        return conf

    def keys(self):
        return self._data.keys()

    def get(self, key: str, module: str = None):
        if module:
            path = module.split('.') + key.split('.')
        else:
            path = key.split('.')

        conf = self._data
        for k in path:
            if not (conf := conf.get(k)):
                return conf
        return conf


def load_config_file(config_file=None):
    if CONF_PATH := config_file:
        pass
    elif CONF_PATH := os.environ.get('BAT_CONFIG_FILE', default=None):
        pass
    elif (conf_path := Path(os.getcwd() + '/config.yaml')).is_file():
        CONF_PATH = conf_path  # dont leave a dirty CONF_PATH variable
    else:
        log.warn(
            "Config File not specified:"
            " create config.yaml,"
            " set environment variable PROJECT_CONFIG to config file path,"
            " or speicfy a config file."
        )
        return {'default': 'none', 'none': 'empty'}

    with open(CONF_PATH) as env_file:
        CONF = yaml.load(env_file, Loader=yaml.BaseLoader)

    return CONF


_missing_config_warning = (
    "Config File not specified:"
    " create config.yaml,"
    " set environment variable PROJECT_CONFIG to config file path,"
    " or speicfy a config file."
)
