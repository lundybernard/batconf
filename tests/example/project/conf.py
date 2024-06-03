from . import ProjectConfig

from batconf.manager import Configuration, ConfigProtocol

from batconf.source import SourceList
from batconf.sources.args import CliArgsConfig, Namespace
from batconf.sources.env import EnvConfig
from batconf.sources.file import FileConfig
from batconf.sources.dataclass import DataclassConfig


def get_config(
    config_class: ConfigProtocol = ProjectConfig,
    cli_args: Namespace = None,
    config_file: FileConfig = None,
    config_file_name: str = None,
    config_env: str = None,
) -> Configuration:
    """Example get_config function

    This function builds a :class:`SouceList`, which defines the configuration
    sources and lookup order.

    :param config_class:  python builtin dataclass
    of type dataclass[dataclass | str]
    :param cli_args:  :class:`Namespace` provided by python's builtin argparse
    :param config_file:
    :param config_file_name:
    :param config_env: Environment id string, ex: 'dev', 'staging', 'yourname'
    used by some sources such as :class:`FileConfig` to
    :return: A batconf :class:`Configuration` instance, used to access config
    values from the :class:`SourceList` using the config_class tree
    or module namespace (these should™ match).
    """

    # Build a prioritized config source list
    config_sources = [
        CliArgsConfig(cli_args) if cli_args else None,
        EnvConfig(),
        (
            config_file
            if config_file
            else FileConfig(config_file_name, config_env=config_env)
        ),
        DataclassConfig(config_class),
    ]

    source_list = SourceList(config_sources)

    return Configuration(source_list, config_class)
