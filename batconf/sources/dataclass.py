from dataclasses import (
    dataclass,
    fields,
    is_dataclass,
    _MISSING_TYPE,
)

from ..source import SourceInterface


class DataclassConfig(SourceInterface):

    def __init__(self, ConfigClass: dataclass):
        '''Extract default values from the Config dataclass
        Properties without defaults are set to None
        '''
        self._root = ConfigClass.__module__
        self._data = dict()

        for field in fields(ConfigClass):
            if is_dataclass(field.type):
                self._data[field.name] = DataclassConfig(field.type)
            elif type(field.default) is _MISSING_TYPE:
                self._data[field.name] = None
            else:
                self._data[field.name] = field.default

    def get(self, key: str, module: str = None):
        if module:
            path = module.split('.') + key.split('.')
            # remove the root module
            for m in self._root.split('.'):
                if m == path[0]:
                    path.pop(0)
        else:
            path = key.split('.')

        conf = self._data
        for k in path:
            if not (conf := conf.get(k)):
                return conf
        return conf
