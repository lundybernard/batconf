import os
from typing import Optional

from ..source import SourceInterface


class EnvConfig(SourceInterface):

    def __init__(self):
        pass

    def get(self, key: str, module: str = None) -> Optional[str]:
        return os.getenv(self.env_name(key, module))

    def env_name(self, key: str, module: str = None) -> str:
        if module:
            path = module.split('.') + key.split('.')
        else:
            path = ['BAT'] + key.split('.')

        return '_'.join(path).upper()
