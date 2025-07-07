![Logo](https://github.com/lundybernard/batconf/blob/main/docs/source/_static/batconf-logo.png?raw=true)

# BatConf

Configuration Management for Python projects, modules, applications,
and microservices.

[![Stable Version](https://img.shields.io/pypi/v/batconf?color=blue)](https://pypi.org/project/batconf/)
[![Downloads](https://img.shields.io/pypi/dm/batconf)](https://pypistats.org/packages/batconf)
[![Build Status](https://github.com/lundybernard/batconf/actions/workflows/tests.yml/badge.svg)](https://github.com/lundybernard/batconf/actions)
[![Documentation Status](https://readthedocs.org/projects/batconf/badge/?version=latest)](https://batconf.readthedocs.io/en/latest/)

![Python 3.9](https://img.shields.io/badge/Python-3.9-blue)
![Python 3.10](https://img.shields.io/badge/Python-3.10-blue)
![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)
![Python 3.13](https://img.shields.io/badge/Python-3.13-blue)

Compose structured hierarchical configurations from multiple sources.
Enable your code to adapt seemlessly to the current context.
Allow users in different contexts to use the config source that works best for
them.

* Hierarchical priority: CLI > Environment > config file > module defaults
* Provides builtin support for common config sources:
    * CLI args
    * Environment Variables
    * Config File (yaml)
    * Config classes with default values
* Easily extendable, add new sources to serve your needs.
* Set reasonable defaults, and override them as needed.
* Designed for 12-factor applications (config via Environment Variables)

Users can create their own config sources
by creating classes that satisfy `batconf.source.SourceInterfaceProto`
(or subclass `batconf.source.SourceInterface`)

The config lookup order is determined by the `SourceList` instance,
which can be adjusted to suit your needs.

## Design Principles

* **Non-Intrusive Integration**: BatConf can be seamlessly incorporated
  into existing projects with minimal code modifications.
    * imports from batconf can be isolated to a single source file
    * Config classes utilize stdlib dataclasses
* **Portability and Modularity**: Modules (sub-modules or entire projects) that
  use batconf configuration
  should be easy to compose and refactor.
    * modules can be easily plugged in to other modules.
    * modules can be easily factored out (into new projects).

## Professional Support

![Tidelift Logo](docs/source/_static/Tidelift_Logos_RGB_Tidelift_Mark_On-White.png)
Professionally supported BatConf is now available.

Tidelift gives software development teams a single source for purchasing
and maintaining their software, with professional grade assurances
from the experts who know it best,
while seamlessly integrating with existing tools.

[Get supported BatConf with the Tidelift subscription](
https://tidelift.com/subscription/pkg/pypi-batconf?utm_source=pypi-batconf&utm_medium=readme
)

## [Example Configuration](tests/example/)

*
REF: [template project example](https://github.com/lundybernard/project_template/blob/main/bat/conf.py)
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

Install the core package:

`pip install .`

Install with Yaml support:

`pip install .[yaml]`

Install with Toml support, for python<=3.11:

`pip install .[toml]`


#### Install with Poetry

install poetry >= 1.1.13

`poetry install`

#### Manual install

install the dev dependencies listed in pyproject.toml


## Dev Guide

### Install dev dependencies (pytest, mypy, etc)

`pip install --group=dev -e .`


## Security contact information

To report a security vulnerability, please use the
[Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.
