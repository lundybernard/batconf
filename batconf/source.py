from abc import ABCMeta, abstractmethod

from typing import Optional, Protocol, Sequence, List


OpStr = Optional[str]


class SourceInterfaceProto(Protocol):
    def get(self, key: str, path: OpStr) -> OpStr:
        pass


class SourceInterface(SourceInterfaceProto, metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str, path: OpStr = None) -> OpStr:
        pass


class SourceList(SourceInterface):

    def __init__(self, sources: Sequence[Optional[SourceInterface]]):
        self._sources: List[SourceInterface] = list(filter(None, sources))

    def get(self, key: str, path: OpStr = None) -> OpStr:
        for source in self._sources:
            if value := source.get(key, path):
                return value
        return None
