import os

from ..source import SourceInterface


class EnvConfig(SourceInterface):

    def __init__(self):
        pass

    def get(self, key: str, module: str = None):
        return os.environ.get(self.env_name(key, module), default=None)

    def env_name(self, key: str, module: str = None):
        if module:
            path = module.split('.') + key.split('.')
        else:
            path = ['BAT'] + key.split('.')

        return '_'.join(path).upper()
