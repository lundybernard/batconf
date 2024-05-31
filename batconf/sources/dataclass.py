from typing import Type, Union, Iterable, Protocol, runtime_checkable, Any

from dataclasses import (
    _MISSING_TYPE,
)

from ..source import SourceInterface, OpStr


class FieldProtocol(Protocol):
    type: Union["ConfigProtocol", Type[str]]
    name: str
    default: Union[str, _MISSING_TYPE]


@runtime_checkable
class ConfigProtocol(Protocol):
    """
    In most cases this should be a dataclass,
    However, any object that provides `__dataclass_fields__` will work
    """
    __dataclass_fields__: dict[str, FieldProtocol]


class DataclassConfig(SourceInterface):

    def __init__(self, ConfigClass: Union[ConfigProtocol, Any]):
        """
        Extract default values from the Config dataclass.
        Properties without defaults are set to None.

        :param ConfigClass: a Config dataclass or :class:`ConfigProtocol` obj
        """
        self._root = ConfigClass.__module__
        self._data: dict = {}

        for field in _fields(ConfigClass):
            if isinstance(field.type, ConfigProtocol):
                self._data[field.name] = DataclassConfig(field.type)
            elif type(field.default) is _MISSING_TYPE:
                self._data[field.name] = None
            else:
                self._data[field.name] = field.default

    def get(self, key: str, module: OpStr = None) -> OpStr:
        if module:
            path = module.split(".") + key.split(".")
            # remove the root module
            for m in self._root.split("."):
                if m == path[0]:
                    path.pop(0)
        else:
            path = key.split(".")

        # Ignore type-hinting in recursion
        conf = self._data
        for k in path:
            if (conf := conf.get(k)) is None:  # type: ignore
                return conf
        return conf  # type: ignore


def _fields(dataclass: ConfigProtocol) -> Iterable[FieldProtocol]:
    for _, v in dataclass.__dataclass_fields__.items():
        yield v
