"""Protocol types and type aliases for use in type annotations.

Import from here when you need to annotate parameters that accept batconf
objects, rather than importing implementation classes directly.

Examples
--------
>>> from batconf.types import ConfigProtocol, SourceInterfaceProto
>>> def get_config(config_class: ConfigProtocol, source: SourceInterfaceProto) -> Configuration:
...     ...
"""

from typing import Protocol, Type, runtime_checkable

from .sources.types import ConfigFileFormats, MissingFileOption


class SourceInterfaceProto(Protocol):
    def get(self, key: str, path: str | None) -> str | None: ...


class SourceListProto(SourceInterfaceProto, Protocol):
    def insert_source(
        self, source: SourceInterfaceProto, index: int = 0
    ) -> None: ...


class FieldProtocol(Protocol):
    type: 'ConfigProtocol | Type[str]'
    name: str
    default: str


@runtime_checkable
class ConfigProtocol(Protocol):
    __dataclass_fields__: dict[str, FieldProtocol]


__all__ = [
    'ConfigProtocol',
    'FieldProtocol',
    'SourceInterfaceProto',
    'SourceListProto',
    'ConfigFileFormats',
    'MissingFileOption',
]
