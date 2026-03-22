from typing import Protocol

from .manager import Configuration
from .source import SourceInterfaceProto, SourceListProto, SourceList


class _InsertableSourceList(Protocol):
    def insert_source(
        self,
        source: SourceInterfaceProto,
        index: int = 0,
    ) -> None: ...


class _HasConfigSources(Protocol):
    _config_sources: SourceListProto


def insert_source(
    cfg: _HasConfigSources,
    source: SourceInterfaceProto,
    index: int = 0,
) -> None:
    """Insert a configuration source into the configuration's source list.

    Configuration sources are queried in order, with lower indices taking
    precedence. By default, new sources are inserted at index 0 (highest
    priority).

    Parameters
    ----------
    cfg : Configuration or ConfigSingleton
        Configuration object or singleton to modify.
    source : SourceInterfaceProto
        Configuration source to insert (e.g., CLI args, environment
        variables, config file).
    index : int, default=0
        Position to insert the source at (0 = highest priority).

    Examples
    --------
    Insert CLI arguments as the highest priority source:

    >>> from batconf.sources.argparse import NamespaceConfig
    >>> from argparse import Namespace
    >>> args = Namespace()
    >>> setattr(args, 'project.key', 'value')
    >>> insert_source(cfg=CFG, source=NamespaceConfig(args))

    Insert a lower priority source:

    >>> insert_source(cfg=CFG, source=env_config, index=2)

    See Also
    --------
    Configuration : Main configuration manager class.
    SourceList : Container that manages configuration sources.
    ConfigSingleton : Singleton proxy for global configuration.
    """
    cfg._config_sources.insert_source(source=source, index=index)


__all__ = [
    'insert_source',
]
