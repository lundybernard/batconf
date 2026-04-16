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
    'FieldP',
    'FileSourceP',
    'SourceInterfaceP',
    'SourceListP',
    'ConfigFileFormats',
    'MissingFileOption',
]

_deprecated: dict[str, str] = {
    'ConfigProtocol': 'ConfigP',
    'FieldProtocol': 'FieldP',
    'SourceInterfaceProto': 'SourceInterfaceP',
    'SourceListProto': 'SourceListP',
}


def __getattr__(name: str):
    if name in _deprecated:
        import warnings
        new = _deprecated[name]
        warnings.warn(
            f'{name!r} is deprecated, use {new!r} instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return globals()[new]
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
