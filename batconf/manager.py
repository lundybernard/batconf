from typing import (
    Any,
    Iterable,
)

from .errors import ConfigValueNotFound
from .source import SourceList
from .types import ConfigP, FieldP, SourceListP


class Configuration:
    """Resolves configuration values from an ordered :class:`SourceList`.

    Values are looked up by walking the ``config_class`` dataclass schema to
    determine the dotted path, then querying each source in the
    :class:`SourceList` in priority order until a value is found.

    Configuration hierarchy (highest to lowest priority):

    1. **Command-line arguments** — passed in via a :class:`NamespaceSource`
    2. **Environment variables** — via :class:`EnvSource`
    3. **Config file** — via :class:`IniSource`, :class:`TomlSource`, etc.
    4. **Dataclass defaults** — values declared on the config schema

    Parameters
    ----------
    source_list : SourceListP
        Ordered collection of configuration sources to query.
    config_class : ConfigP
        Dataclass whose fields define the configuration schema.
    path : str or None, default=None
        Dotted namespace path for this configuration node. An absent or
        empty path mounts the schema at the root of the namespace, and
        every sub-configuration mounts under its field name.

    Examples
    --------
    >>> cfg = Configuration(
    ...     source_list=SourceList(sources=[EnvSource(), IniSource(file_path='config.ini')]),
    ...     config_class=AppConfigSchema,
    ... )
    >>> cfg.database.host
    'localhost'
    """

    def __init__(
        self,
        source_list: SourceListP,
        config_class: ConfigP,
        path: str | None = None,
    ):
        self._config_sources = source_list
        self._config_class = config_class
        self.__path = path

        self._sub_configs: dict[str, Configuration] = {
            f.name: Configuration(
                source_list=source_list,
                config_class=f.type,
                path=self._path_of(f.name),
            )
            for f in _fields(self._config_class)
            if isinstance(f.type, ConfigP)
        }

        self._default_values: dict[str, str] = {
            f.name: f.default
            for f in _fields(self._config_class)
            if isinstance(f.default, str)
        }

    def __getattr__(self, name: str) -> Any:
        if cfg := self._sub_configs.get(name, None):
            return cfg
        return self._get_config_opt(name)

    def __getitem__(self, name: str) -> Any:
        return self.__getattr__(name)

    def _get_config_opt(self, key: str) -> str:
        if value := self._config_sources.get(key, path=self._path):
            return value

        if value := self._default_values.get(key, None):
            return value

        dotted = self._path_of(key)

        raise ConfigValueNotFound(
            'required configuration value not found.\n'
            f' please provide {key}'
            ' as a commandline argument\n'
            f' or add {dotted}'
            ' to your config file\n'
            f' or add {dotted.replace(".", "_").upper()}'
            ' to your Environment, after any EnvSource prefix'
        )

    @property
    def _path(self) -> str:
        return self.__path or ''

    def _path_of(self, name: str) -> str:
        """Return the path ``name`` mounts at under this node."""
        return f'{self._path}.{name}' if self._path else name

    def __str__(self) -> str:
        header = f'{self._path} ' if self._path else ''
        repr_str = [f'{header}{self._config_class}:']
        repr_str += _configuration_repr(configuration=self, level=1)
        repr_str.append(str(self._config_sources))
        return '\n'.join(repr_str)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'source_list={repr(self._config_sources)}, '
            f'config_class={repr(self._config_class)})'
        )


# Replacement for dataclasses.fields, typed for ConfigP
def _fields(dataclass: ConfigP) -> Iterable[FieldP]:
    for _, v in dataclass.__dataclass_fields__.items():
        yield v


def _configuration_repr(
    configuration: Configuration,
    level: int,
) -> list[str]:
    attrs = []
    children = []

    for field in _fields(configuration._config_class):
        if isinstance(field.type, ConfigP):
            children.append(
                ''.join(('    |' * level, f'- {field.name} {field.type}:'))
            )
            children += _configuration_repr(
                getattr(configuration, field.name),
                level + 1,
            )
        else:
            strings = (
                '    |' * level,
                f'- {field.name}: ',
                f'"{getattr(configuration, field.name, "MISSING_VALUE")}"',
            )
            attrs.append(''.join(strings))

    return attrs + children
