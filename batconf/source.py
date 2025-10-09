from abc import ABCMeta, abstractmethod

from typing import Protocol, Sequence


class SourceInterfaceProto(Protocol):
    def get(self, key: str, path: str | None) -> str | None: ...


class SourceInterface(SourceInterfaceProto, metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str, path: str | None = None) -> str | None:
        pass


class SourceList(SourceInterface):
    def __init__(self, sources: Sequence[SourceInterface | None]) -> None:
        self._sources: list[SourceInterface] = list(filter(None, sources))

    def get(self, key: str, path: str | None = None) -> str | None:
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
