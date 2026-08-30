"""Protocol types and type aliases for use in type annotations.

Import from here when you need to annotate parameters that accept batconf
objects, rather than importing implementation classes directly.

Examples
--------
>>> from batconf.types import ConfigP, SourceInterfaceP
>>> def get_config(config_class: ConfigP, source: SourceInterfaceP) -> Configuration:
...     ...
"""

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

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
    # a live class, or its annotation string. Configuration reads a
    # nested schema from the class; every other field is a leaf.
    type: type | str
    name: str
    default: object


@runtime_checkable
class ConfigP(Protocol):
    # read-only: a dict member would be invariant, and no dataclass
    # would satisfy the protocol
    @property
    def __dataclass_fields__(self) -> Mapping[str, FieldP]: ...


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
