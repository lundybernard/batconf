from abc import ABCMeta, abstractmethod


class SourceInterface(metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str, path: str = None):
        pass


class SourceList:

    def __init__(self, sources: 'list[SourceInterface]'):
        self._sources = list(filter(None, sources))

    def get(self, key: str, path: str = None):
        for source in self._sources:
            if value := source.get(key, path):
                return value
        return None
