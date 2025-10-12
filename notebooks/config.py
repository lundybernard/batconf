from typing import Any, Sequence

from pathlib import Path

from batconf.manager import Configuration, ConfigProtocol
from batconf.source import SourceList, SourceInterface
from batconf.sources.ini import IniConfig


# === Configuration Schema === #
from dataclasses import dataclass


@dataclass
class ClientConfigSchema:
    doc: str
    address: str
    uname: str


@dataclass
class NotebooksConfigSchema:
    client: ClientConfigSchema
    doc: str
    opt1: str
    opt2: str = 'opt2 default'


# Get the absolute path to the notebooks config.yaml file
_notebooks_dir = Path(__file__).parent
CONFIG_FILE_NAME = str(_notebooks_dir / 'config.ini')


def get_config(
    config_class: ConfigProtocol | Any = NotebooksConfigSchema,
    cfg_path: str = 'notebooks',
    config_file: SourceInterface | None = None,
    config_file_name: str = CONFIG_FILE_NAME,
    config_env: str | None = None,
) -> Configuration:
    """Example get_config function

    This function builds a :class:`SouceList`, which defines the configuration
    sources and lookup order.  Then uses it to create a :class:`Configuration`
    which provides access to the configuration values.

    :param config_class: The BatConf configuration schema
    python builtin dataclass of type dataclass[dataclass | str].
    Type-hint includes :class:`Any` because mypy does not currently recognize
    the dataclass produced by @dataclass as satisfying the ConfigProtocol.
    :param cfg_path: :class:`String` The name of the config tree root
    for your project.
    :param cli_args: :class:`Namespace` provided by python's builtin argparse
    :param config_file: Optional config file source injection.  Initialize
    any `batconf.sources.` *Config class
    [`IniConfig`, `TomlConfig`, `YamlConfig`],
    and use it as the config file source
    :param config_file_name:
    :param config_env: Environment id string, ex: 'dev', 'staging', 'yourname'
    used by some sources such as :class:`YamlConfig` to
    :return: A batconf :class:`Configuration` instance, used to access config
    values from the :class:`SourceList` using the config_class tree
    or module namespace (these should™ match).
    """

    # Build a prioritized config source list
    config_sources: Sequence[SourceInterface | None] = [
        (
            config_file
            if config_file
            else IniConfig(config_file_name, config_env=config_env)
        ),
    ]

    source_list = SourceList(config_sources)

    return Configuration(source_list, config_class, path=cfg_path)
