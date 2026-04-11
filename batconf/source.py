from abc import ABCMeta, abstractmethod

from typing import Sequence

from .types import SourceInterfaceP, SourceListP


class SourceInterface(SourceInterfaceP, metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str, path: str | None = None) -> str | None:
        pass


class SourceList:
    """An ordered list of configuration sources.

    Sources are queried in order; the first non-``None`` value returned wins.
    ``None`` entries in the constructor sequence are silently filtered out,
    making it easy to conditionally include sources.

    Parameters
    ----------
    sources : Sequence[SourceInterfaceP | None]
        Ordered sequence of configuration sources. Earlier entries take
        precedence over later ones.

    Examples
    --------
    >>> source_list = SourceList(sources=[NamespaceSource(args), EnvSource(), IniSource(file_path='config.ini')])
    """

    def __init__(self, sources: Sequence[SourceInterfaceP | None]) -> None:
        self._sources: list[SourceInterfaceP] = list(filter(None, sources))

    def get(self, key: str, path: str | None = None) -> str | None:
        for source in self._sources:
            if value := source.get(key, path):
                return value
        return None

    def insert_source(
        self,
        source: SourceInterfaceP,
        index: int = 0,
    ) -> None:
        self._sources.insert(index, source)

    def __str__(self) -> str:
        srs = (f'{src},' for src in self._sources)
        srs_strs = '\n    '.join(srs)
        return f'SourceList=[\n    {srs_strs}\n]'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(sources={self._sources})'
