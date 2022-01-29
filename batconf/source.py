from abc import ABCMeta, abstractmethod

from typing import Optional, Protocol, Sequence


Ostr = Optional[str]


class SourceInterfaceProto(Protocol):
    def get(self, key: str, path: Ostr) -> Ostr:
        pass


class SourceInterface(SourceInterfaceProto, metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str, path: Ostr = None) -> Ostr:
        pass


class SourceList(SourceInterface):

    def __init__(self, sources: Sequence[Optional[SourceInterface]]) -> None:
        self._sources: list[SourceInterface] = list(filter(None, sources))

    def get(self, key: str, path: Ostr = None) -> Ostr:
        for source in self._sources:
            if value := source.get(key, path):
                return value
        return None
