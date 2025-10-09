from typing import (
    Type,
    Iterable,
    Protocol,
    runtime_checkable,
    Any,
    cast,
    TypeAlias,
)

from dataclasses import _MISSING_TYPE

from ..source import SourceInterface


class FieldProtocol(Protocol):
    type: 'ConfigProtocol | Type[str]'
    name: str
    default: str | _MISSING_TYPE


@runtime_checkable
class ConfigProtocol(Protocol):
    """
    In most cases this should be a dataclass,
    However, any object that provides `__dataclass_fields__` will work
    """

    __dataclass_fields__: dict[str, FieldProtocol]


class DataclassConfig(SourceInterface):
    def __init__(
        self, ConfigClass: ConfigProtocol | Any, path: str | None = None
    ):
        """Extract default values from the Config dataclass.
        Properties without defaults are set to None.

        :param ConfigClass: a Config dataclass or :class:`ConfigProtocol` obj
        """
        self._root = path if path else ConfigClass.__module__
        self._data: _DATA_DICT_TYPE = {}

        for field in _fields(ConfigClass):
            if isinstance(field.type, ConfigProtocol):
                self._data[field.name] = DataclassConfig(field.type)
            elif type(field.default) is _MISSING_TYPE:
                self._data[field.name] = None
            else:
                self._data[field.name] = cast(str, field.default)

    def get(self, key: str, module: str | None = None) -> str | None:
        if module:
            path = module.split('.') + key.split('.')
            # remove the root module
            for m in self._root.split('.'):
                if m == path[0]:
                    path.pop(0)
        else:
            path = key.split('.')

        # TODO: Needs a thorough review
        # The difficulty in typing this indicates some potential issues
        # like unexpected return values.
        conf: _DATA_DICT_TYPE | str | None = self._data
        for k in path:
            if (conf := conf.get(k)) is None:  # type: ignore
                return conf
        return conf  # type: ignore


def _fields(dataclass: ConfigProtocol) -> Iterable[FieldProtocol]:
    for _, v in dataclass.__dataclass_fields__.items():
        yield v


_VALUES: TypeAlias = DataclassConfig | str | None
_DATA_DICT_TYPE: TypeAlias = dict[str, _VALUES]
