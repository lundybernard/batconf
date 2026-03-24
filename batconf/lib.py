from typing import Callable, Protocol
from functools import cached_property

from .manager import Configuration
from .source import SourceList
from .types import SourceInterfaceProto, SourceListProto


class ConfigSingleton:
    """Global singleton-style proxy for application configuration.

    Provides a single shared :class:`Configuration` object
    across the application. The configuration is initialized from
    ``get_config_fn`` and then reused wherever the instance is imported.

    Lazy loading is supported as a convenience: the underlying
    :class:`Configuration` is created only when first accessed.

    Parameters
    ----------
    get_config_fn : Callable
        Zero-argument callable that returns a
        :class:`~.manager.Configuration` instance.

    Notes
    -----
    The cached configuration can be refreshed by calling :meth:`_reset`.

    Examples
    --------
    >>> cfg = ConfigSingleton(get_config_fn=get_config)
    >>> cfg.some_option
    'value'

    Using a partially applied config factory::

    >>> from functools import partial

    >>> CFG = ConfigSingleton(
    >>>        get_config_fn=partial(get_config, env="prod", debug=False)
    >>>    )
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
    'ConfigSingleton',
    'insert_source',
]
