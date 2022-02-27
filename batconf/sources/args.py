from argparse import Namespace

from ..source import SourceInterface, Ostr


class CliArgsConfig(SourceInterface):

    def __init__(self, args: Namespace) -> None:
        self._data = args

    def get(self, key: str, module: str = None) -> Ostr:
        key = key.split('.')[-1]

        return getattr(self._data, key, None)
