from typing import (
    Optional,
    Union,
    Protocol,
    Dict,
    runtime_checkable,
    Iterable,
    Type,
    Any,
)

from .source import SourceList


OpStr = Optional[str]
ConfigValue = Union["ConfigProtocol", Type[str]]


class FieldProtocol(Protocol):
    type: ConfigValue
    name: str


@runtime_checkable
class ConfigProtocol(Protocol):
    __dataclass_fields__: Dict[str, FieldProtocol]


ConfigRet = Union["Configuration", str, Any]


class Configuration:
    """
    Args:
        source_list: A :class:`SourceList` instance,
            contains configuation sources
            which are searched for config string values
        config_class: A dataclass Class object (not instantiated).
            Used to provide a map to sub-configs,
            and the __module__ value for path namespace mapping

    Recommended Configuration Hierarchy:

    The SourceList determines the actual Hierarchy,
    and allows you to configure sources for your specific needs.

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
        may be set in the config specification
    """

    def __init__(
        self,
        source_list: SourceList,
        config_class: Union[ConfigProtocol, Any],
    ):
        self._config_sources = source_list
        self._config_class = config_class

        for f in _fields(self._config_class):
            if isinstance(f.type, ConfigProtocol):
                setattr(
                    self,
                    f.name,
                    Configuration(
                        source_list=source_list,
                        config_class=f.type
                        ),
                )

    def __getattr__(self, name: str) -> Any:
        """
        :param name: :class:`str`. Name of the attribute.
        :return: :class:`Configuration` instance or configuration :class:`str`
            if the attribute value is a terminal configuration value
            and not a sub-configuration.
        """

        return self._get_config_opt(name, self._mod_)

    def _get_config_opt(self, key: str, path: OpStr = None) -> Any:
        if value := self._config_sources.get(key, path=path):
            return value

        raise AttributeError(
            "required configuration value not found.\n"
            f" please provide {key}"
            " as a commandline argument\n"
            f" or add {self._config_class.__module__}.{key}"
            " to your config file\n"
            f' or add {self._mod_.replace(".", "_").upper()}_{key.upper()}'
            " to your Environment"
        )

    @property
    def _mod_(self) -> str:
        return self._config_class.__module__


# Replacement for dataclasses.fields, typed for ConfigProtocol
def _fields(dataclass: ConfigProtocol) -> Iterable[FieldProtocol]:
    for _, v in dataclass.__dataclass_fields__.items():
        yield v
