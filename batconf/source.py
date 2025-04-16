from abc import ABCMeta, abstractmethod

from typing import Optional, Protocol, Sequence, List


OpStr = Optional[str]


class SourceInterfaceProto(Protocol):
    def get(self, key: str, path: OpStr) -> OpStr: ...


class SourceInterface(SourceInterfaceProto, metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str, path: OpStr = None) -> OpStr:
        pass


class SourceList(SourceInterface):
    def __init__(self, sources: Sequence[Optional[SourceInterface]]) -> None:
        self._sources: List[SourceInterface] = list(filter(None, sources))

    def get(self, key: str, path: OpStr = None) -> OpStr:
        for source in self._sources:
            if value := source.get(key, path):
                return value
        return None

    def __str__(self) -> str:
        srs = (f'{src},' for src in self._sources)
        srs_strs = '\n    '.join(srs)
        return f'SourceList=[\n    {srs_strs}\n]'

    def __repr__(self) -> str:
        return f'SourceList(sources={self._sources})'
