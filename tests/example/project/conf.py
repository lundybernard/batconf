from typing import Any, Sequence

from os import path

from batconf.manager import Configuration, ConfigProtocol

from batconf.source import SourceList, SourceInterface
from batconf.sources.argparse import NamespaceConfig, Namespace

# from batconf.sources.args import CliArgsConfig, Namespace
from batconf.sources.env import EnvConfig
from batconf.sources.ini import IniConfig
from .submodule import MyClient


# === Configuration Schema === #
from dataclasses import dataclass


@dataclass
class SubmoduleConfigSchema:
    client: MyClient.Config


@dataclass
class ClientConfigurationsSchema:
    """
    .. versionchanged:: 0.2
       Added support for multiple configurations from single Schema.
    """

    clientA: MyClient.Config
    clientB: MyClient.Config


@dataclass
class ProjectConfigSchema:
    submodule: SubmoduleConfigSchema
    clients: ClientConfigurationsSchema


"""
Use of a default configuration file location bears some careful consideration
Think carefully about the location of a default ~/.cfg/yourapp/ /etc/yourapp/ ?
  On Linux systems you may want both system and user config files.
  Windows has its own concept of appdata to conform to.
Your choice in configuration file location is entirely up to you,
  and may depend heavily on your application's needs.

Let us know if you would find some default settings 
based on OS standards useful.
"""

# Get the absolute path to the test config.yaml file
_example_project_dir = path.dirname(path.realpath(__file__))
CONFIG_FILE_NAME = path.join(_example_project_dir, '../config.ini')


def get_config(
    config_class: ConfigProtocol | Any = ProjectConfigSchema,
    cfg_path: str = 'project',
    cli_args: Namespace | None = None,
    config_file: SourceInterface | None = None,
    config_file_name: str = CONFIG_FILE_NAME,
    config_env: str | None = None,
) -> Configuration:
    """Example get_config function

    This function builds a :class:`SouceList`, which defines the configuration
    sources and lookup order.

    :param config_class: python builtin dataclass
    of type dataclass[dataclass | str].
    Type-hint includes :class:`Any` because mypy does not currently recognize
    the dataclass produced by @dataclass as satisfying the ConfigProtocol.
    :param cli_args: :class:`Namespace` provided by python's builtin argparse
    :param config_file:
    :param config_file_name:
    :param config_env: Environment id string, ex: 'dev', 'staging', 'yourname'
    used by some sources such as :class:`YamlConfig` to
    :return: A batconf :class:`Configuration` instance, used to access config
    values from the :class:`SourceList` using the config_class tree
    or module namespace (these should™ match).
    """

    # Build a prioritized config source list
    config_sources: Sequence[SourceInterface | None] = [
        NamespaceConfig(cli_args) if cli_args else None,
        EnvConfig(),
        (
            config_file
            if config_file
            else IniConfig(config_file_name, config_env=config_env)
        ),
    ]

    source_list = SourceList(config_sources)

    return Configuration(source_list, config_class, path=cfg_path)
