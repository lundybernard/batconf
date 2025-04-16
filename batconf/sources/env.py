import os

from ..source import SourceInterface, OpStr


class EnvConfig(SourceInterface):
    def __init__(self) -> None:
        pass

    def get(self, key: str, module: OpStr = None) -> OpStr:
        return os.getenv(self.env_name(key, module))

    def env_name(self, key: str, module: OpStr = None) -> str:
        if module:
            path = module.split('.') + key.split('.')
        else:
            path = ['BAT'] + key.split('.')

        return '_'.join(path).upper()
