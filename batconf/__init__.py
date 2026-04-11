"""batconf — layered configuration for Python applications.

Public API
----------
Configuration
    The main configuration manager. Resolves values from an ordered
    :class:`SourceList` against a dataclass-based config schema.
ConfigSingleton
    Lazy, singleton-style proxy around a :class:`Configuration` instance,
    suitable for use as a module-level global.
SourceList
    Ordered collection of configuration sources.
insert_source
    Helper to insert a new source into an existing configuration at runtime.

Sources
-------
NamespaceSource
    Reads from an :class:`argparse.Namespace` object using fully-qualified
    dotted key paths (e.g. ``project.host``).
EnvSource
    Reads from environment variables.
IniSource
    Reads from INI files.
TomlSource
    Reads from TOML files.
YamlSource
    Reads from YAML files.

Type annotations
----------------
See :mod:`batconf.types` for Protocol types used in type hints.
"""

from .lib import insert_source, ConfigSingleton
from .manager import Configuration
from .source import SourceList
from .sources.argparse import NamespaceConfig as NamespaceSource, Namespace
from .sources.env import EnvConfig as EnvSource
from .sources.ini import IniConfig as IniSource
from .sources.toml import TomlConfig as TomlSource
from .sources.yaml import YamlSource

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
