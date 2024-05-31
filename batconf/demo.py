from dataclasses import dataclass, Field, fields, is_dataclass
from typing import Union, Protocol, Dict, Any, runtime_checkable, cast


ConfigValue = Union["ConfigProtocol", str]


@runtime_checkable
class FieldProtocol(Protocol):
    type: ConfigValue
    name: str


@runtime_checkable
class ConfigProtocol(Protocol):
    # __dataclass_fields__: Dict[str, Field]
    __dataclass_fields__: Dict[str, Field[ConfigValue]]


class Configuration:

    def __init__(self, config_class: ConfigProtocol):
        self._config_class = config_class

        for f in fields(self._config_class):
            # if is_dataclass(f.type):
            # if hasattr(f.type, '__dataclass_fields__'):
            if isinstance(f.type, ConfigProtocol):
                setattr(
                    self,
                    f.name,
                    Configuration(
                        config_class=f.type
                        # config_class=cast(ConfigProtocol, f.type)
                    ),
                )


@dataclass
class ConfigClass:
    key: str = "v_1"


@dataclass
class GlobalConfig:
    TestModule: ConfigClass
    config_file: str = "GlobalConfig.yaml"


conf = Configuration(GlobalConfig)
