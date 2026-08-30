"""Protocol types and type aliases for use in type annotations.

Import from here when you need to annotate parameters that accept batconf
objects, rather than importing implementation classes directly.

Examples
--------
>>> from batconf.types import ConfigP, SourceInterfaceP
>>> def get_config(config_class: ConfigP, source: SourceInterfaceP) -> Configuration:
...     ...
"""

from typing import Protocol, Type, runtime_checkable

from .sources.types import (
    ConfigFileFormats,
    FILE_FORMATS,
    FileSourceP,
    MissingFileOption,
    SourceInterfaceP,
)


class SourceListP(SourceInterfaceP, Protocol):
    def insert_source(
        self, source: SourceInterfaceP, index: int = 0
    ) -> None: ...


class FieldP(Protocol):
    type: 'ConfigP | Type[str]'
    name: str
    default: str


@runtime_checkable
class ConfigP(Protocol):
    __dataclass_fields__: dict[str, FieldP]


__all__ = [
    'ConfigP',
    'ConfigFileFormats',
    'FieldP',
    'FILE_FORMATS',
    'FileSourceP',
    'MissingFileOption',
    'SourceInterfaceP',
    'SourceListP',
]
