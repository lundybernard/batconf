from argparse import Namespace

from ..source import SourceInterface


class CliArgsConfig(SourceInterface):

    def __init__(self, args: Namespace):
        self._data = args

    def get(self, key: str, module: str = None):
        key = key.split('.')[-1]

        return getattr(self._data, key, None)
