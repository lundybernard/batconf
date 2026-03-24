from typing import Callable, Protocol
from functools import cached_property

from .manager import Configuration
from .source import SourceList
from .types import SourceInterfaceProto, SourceListProto


class ConfigSingleton:
    """Lazy singleton proxy for a :class:`~.manager.Configuration` instance.

    Wraps a ``get_config_fn`` factory and creates the underlying
    :class:`~.manager.Configuration` on first attribute access, then caches
    it for subsequent accesses. Importing the same ``ConfigSingleton``
    instance in multiple modules shares a single configuration object across
    the application.

    Parameters
    ----------
    get_config_fn : Callable[[], Configuration]
        Callable that returns a :class:`~.manager.Configuration` instance.
        Use :func:`functools.partial` to pre-fill any arguments.

    Examples
    --------
    >>> CFG = ConfigSingleton(get_config_fn=get_config)
    >>> CFG.some_option
    'value'

    Using a partially applied config factory:

    >>> from functools import partial
    >>> CFG = ConfigSingleton(
    ...     get_config_fn=partial(get_config, config_env='prod')
    ... )
    """

    def __init__(self, get_config_fn: Callable) -> None:
        self._get_cfg = get_config_fn

    @cached_property
    def _cfg(self) -> Configuration:
        return self._get_cfg()

    def _reset(self) -> None:
        self._cfg = self._get_cfg()

    def __getattr__(self, name: str):
        return getattr(self._cfg, name)

    def __str__(self) -> str:
        return str(self._cfg)

    def __repr__(self) -> str:
        return repr(self._cfg)


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

    >>> from batconf import NamespaceSource
    >>> from argparse import Namespace
    >>> args = Namespace()
    >>> setattr(args, 'project.key', 'value')
    >>> insert_source(cfg=CFG, source=NamespaceSource(namespace=args))

    Insert a lower priority source:

    >>> insert_source(cfg=CFG, source=env_source, index=2)

    See Also
    --------
    Configuration : Main configuration manager class.
    SourceList : Container that manages configuration sources.
    ConfigSingleton : Singleton proxy for global configuration.
    """
    cfg._config_sources.insert_source(source=source, index=index)


__all__ = [
    'ConfigSingleton',
    'insert_source',
]
