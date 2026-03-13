import os

from ..source import SourceInterface


class EnvConfig(SourceInterface):
    def __init__(self) -> None:
        pass

    def get(self, key: str, module: str | None = None) -> str | None:
        return os.getenv(self.env_name(key, module))

    def env_name(self, key: str, module: str | None = None) -> str:
        if module:
            path = module.split('.') + key.split('.')
        else:
            path = ['BAT'] + key.split('.')

        return '_'.join(path).upper()

    def __str__(self):
        return f'Environment Variables: {repr(self)}'

    def __repr__(self):
        return f'{self.__class__.__name__}()'
