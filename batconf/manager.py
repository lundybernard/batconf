from typing import (
    Optional,
    Union,
    Protocol,
    Dict,
    List,
    runtime_checkable,
    Type,
    Any,
    Iterable,
)

from .source import SourceList


OpStr = Optional[str]


class FieldProtocol(Protocol):
    type: Union['ConfigProtocol', Type[str]]
    name: str
    default: str


@runtime_checkable
class ConfigProtocol(Protocol):
    __dataclass_fields__: Dict[str, FieldProtocol]


ConfigRet = Union['Configuration', str]


class Configuration:
    """
    Input: an application config in dictionary form

    Configuration Hierarchy:
    1. Command line arguments
        any argument passed in via command line superseeds all other configs
        this must be passed to the Configuration object by the cli parser
    2. Environment Variables
        Any environment variable with the format BAT_SECTION_SUBSECTION_KEY
        will override the value of configuration.section.subsection.key
    3. Config File
        User defined config file,
        a default file in the current working directory may be set
        the config file may be specified as a cli arg
        the config file path may be set to the BAT_CONFIG_FILE ENV variable
    4. Default Values
        default values may be set in the config specification
    """

    def __init__(
        self,
        source_list: SourceList,
        config_class: Union[ConfigProtocol, Any],
        path: OpStr = None,
    ):
        self._config_sources = source_list
        self._config_class = config_class
        self.__path = path

        self._sub_configs: Dict[str, Configuration] = {
            f.name: Configuration(
                source_list=source_list,
                config_class=f.type,
                path=f'{self._path}.{f.name}',
            )
            for f in _fields(self._config_class)
            if isinstance(f.type, ConfigProtocol)
        }

        self._default_values: Dict[str, str] = {
            f.name: f.default
            for f in _fields(self._config_class)
            if isinstance(f.default, str)
        }

    def __getattr__(self, name: str):  # -> Union[str, 'Configuration']:
        if cfg := self._sub_configs.get(name, None):
            return cfg
        return self._get_config_opt(name)

    def _get_config_opt(self, key: str) -> str:
        if value := self._config_sources.get(key, path=self._path):
            return value

        if value := self._default_values.get(key, None):
            return value

        raise AttributeError(
            'required configuration value not found.\n'
            f' please provide {key}'
            ' as a commandline argument\n'
            f' or add {self._path}.{key}'
            ' to your config file\n'
            f' or add {self._path.replace(".", "_").upper()}_{key.upper()}'
            ' to your Environment'
        )

    @property
    def _path(self) -> str:
        return self.__path if self.__path else self._module

    @property
    def _module(self) -> str:
        return self._config_class.__module__

    def __str__(self) -> str:
        repr_str = [f'{self._path} {self._config_class}:']
        repr_str += _configuration_repr(configuration=self, level=1)
        repr_str.append(str(self._config_sources))
        return '\n'.join(repr_str)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'source_list={repr(self._config_sources)}, '
            f'config_class={repr(self._config_class)})'
        )


# Replacement for dataclasses.fields, typed for ConfigProtocol
def _fields(dataclass: ConfigProtocol) -> Iterable[FieldProtocol]:
    for _, v in dataclass.__dataclass_fields__.items():
        yield v


def _configuration_repr(
    configuration: Configuration,
    level: int,
) -> List[str]:
    attrs = []
    children = []

    for field in _fields(configuration._config_class):
        if isinstance(field.type, ConfigProtocol):
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
