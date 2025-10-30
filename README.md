![Logo](https://github.com/lundybernard/batconf/blob/main/docs/source/_static/batconf-logo.png?raw=true)

# BatConf

Configuration Management for Python projects, modules, applications,
and microservices.

[![Stable Version](https://img.shields.io/pypi/v/batconf?color=blue)](https://pypi.org/project/batconf/)
[![Downloads](https://img.shields.io/pypi/dm/batconf)](https://pypistats.org/packages/batconf)
[![Build Status](https://github.com/lundybernard/batconf/actions/workflows/tests.yml/badge.svg)](https://github.com/lundybernard/batconf/actions)
[![Documentation Status](https://readthedocs.org/projects/batconf/badge/?version=latest)](https://batconf.readthedocs.io/en/latest/)
[![Python](https://img.shields.io/pypi/pyversions/batconf)](https://pypi.org/pypi/batconf/)


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
Check out our [Quick Start Guide](https://batconf.readthedocs.io/en/latest/quickstart.html)

and the example project in [tests/example/](/tests/example) 
  which includes tests and documentation.


## Install Instructions

Install the core package:

`pip install .`

Install with Yaml support:

`pip install .[yaml]`

Install with Toml support, for python<=3.11:

`pip install .[toml]`

### Adding BatConf to your project requirements
```toml
[project]
dependencies = [
    'batconf',
]
```

Including optional extras, like Yaml:

```toml
[project]
dependencies = [
    'batconf[yaml]',
]
```


## Dev Guide

### Install dev dependencies (pytest, mypy, etc)

`pip install --group=dev -e .`


## Security contact information

To report a security vulnerability, please use the
[Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.
