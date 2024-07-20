# BatConf: configuratoin framework for python projects
[![Stable Version](https://img.shields.io/pypi/v/batconf?color=blue)](https://pypi.org/project/batconf/)
[![Downloads](https://img.shields.io/pypi/dm/batconf)](https://pypistats.org/packages/batconf)
[![Build Status](https://github.com/lundybernard/batconf/actions/workflows/tests.yml/badge.svg)](https://github.com/lundybernard/batconf/actions)


![Python 3.8](https://img.shields.io/badge/Python-3.8-blue)
![Python 3.9](https://img.shields.io/badge/Python-3.9-blue)
![Python 3.10](https://img.shields.io/badge/Python-3.10-blue)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)

Designed to provide 12-factor compliant configuration management
for python microservices, applications, and automation tools.

Provides builtin support for hierarchical configuration via:
* CLI args
* Environment Variables
* Config File (yaml)
* Config classes with default values

Users can create their own config sources
by creating classes that satisfy `batconf.source.SourceInterfaceProto`
(or subclass `batconf.source.SourceInterface`)

The config lookup order is determined by the `SourceList` instance,
which can be adjusted to suit your needs.

## [Example Configuration](tests/example/)
* REF: [template project example](https://github.com/lundybernard/project_template/blob/main/bat/conf.py)
* [tests/example/](/tests/example) contains an example project and tests
with documentation.

Most projects can copy this example with minimal modification.

```python
from bat import GlobalConfig

from batconf.manager import Configuration, ConfigProtocol

from batconf.source import SourceList
from batconf.sources.args import CliArgsConfig, Namespace
from batconf.sources.env import EnvConfig
from batconf.sources.file import FileConfig
from batconf.sources.dataclass import DataclassConfig


def get_config(
    # Known issue: https://github.com/python/mypy/issues/4536
    config_class: ConfigProtocol = GlobalConfig,  # type: ignore
    cli_args: Namespace = None,
    config_file: FileConfig = None,
    config_file_name: str = None,
    config_env: str = None,
) -> Configuration:

    # Build a prioritized config source list
    config_sources = [
        CliArgsConfig(cli_args) if cli_args else None,
        EnvConfig(),
        config_file if config_file else FileConfig(
            config_file_name, config_env=config_env
        ),
        DataclassConfig(config_class),
    ]

    source_list = SourceList(config_sources)

    return Configuration(source_list, config_class)
```
### GlobalConfig and Config classes
the `GlobalConfig` class is a python `dataclass`, used for namespacing,
and providing a structured configuration tree.
Its attributes should be other Config dataclasses for sub-modules.

```python
from dataclasses import dataclass
from .example import Config


@dataclass
class GlobalConfig:
    # example module with configuration dataclass
    example: Config
```


## Install Instructions
`pip install .`

#### Install with Poetry
install poetry >= 1.1.13

`poetry install`

#### Manual install
install the dev dependencies listed in pyproject.toml


## Dev Guide
### Install dev dependencies (pytest, mypy, etc)
`pip install -e .[dev]`

### macos/zsh:
`pip install -e ".[dev]"`

## Design Principles
* **Non-Intrusive Integration**: BatConf can be seamlessly incorporated 
  into existing projects with minimal code modifications.
  * imports from batconf can be isolated to a single source file
  * Config classes utilize stdlib dataclasses
* **Portability and Modularity**: Modules (sub-modules or entire projects) that use batconf configuration
  should be easy to compose and refactor.
  * modules can be easily plugged in to other modules.
  * modules can be easily factored out (into new projects).
