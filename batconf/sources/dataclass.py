from dataclasses import (
    fields,
    _MISSING_TYPE,
)

from ..source import SourceInterface, Ostr
from ..manager import ConfigProtocol


class DataclassConfig(SourceInterface):

    def __init__(self, ConfigClass: ConfigProtocol):
        '''Extract default values from the Config dataclass
        Properties without defaults are set to None
        '''
        self._root = ConfigClass.__module__
        self._data: dict = {}

        for field in fields(ConfigClass):
            if isinstance(field.type, ConfigProtocol):
                self._data[field.name] = DataclassConfig(field.type)
            elif type(field.default) is _MISSING_TYPE:
                self._data[field.name] = None
            else:
                self._data[field.name] = field.default

    def get(self, key: str, module: Ostr = None) -> Ostr:
        if module:
            path = module.split('.') + key.split('.')
            # remove the root module
            for m in self._root.split('.'):
                if m == path[0]:
                    path.pop(0)
        else:
            path = key.split('.')

        # Ignore type-hinting in recursion
        conf = self._data
        for k in path:
            if (conf := conf.get(k)) is None:  # type: ignore
                return conf
        return conf  # type: ignore
