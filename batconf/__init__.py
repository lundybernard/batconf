from .lib import insert_source, ConfigSingleton
from .manager import Configuration
from .source import SourceList
from .sources.argparse import NamespaceConfig as NamespaceSource, Namespace
from .sources.env import EnvConfig as EnvSource
from .sources.ini import IniConfig as IniSource
from .sources.toml import TomlConfig as TomlSource
from .sources.yaml import YamlConfig as YamlSource

__all__ = [
    # Core
    'Configuration',
    'ConfigSingleton',
    'SourceList',
    'insert_source',
    # Sources
    'NamespaceSource',
    'Namespace',  # argparse.Namespace, paired with NamespaceSource
    'EnvSource',
    'IniSource',
    'TomlSource',
    'YamlSource',
]
