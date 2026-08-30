![Logo](https://github.com/lundybernard/batconf/blob/main/docs/source/_static/batconf-logo.png?raw=true)

# BatConf

Configuration Management for Python projects, modules, applications,
and microservices.

[![Stable Version](https://img.shields.io/pypi/v/batconf?color=blue)](https://pypi.org/project/batconf/)
[![Downloads](https://img.shields.io/pypi/dm/batconf)](https://pypistats.org/packages/batconf)
[![Build Status](https://github.com/lundybernard/batconf/actions/workflows/tests.yml/badge.svg)](https://github.com/lundybernard/batconf/actions)
[![Documentation Status](https://readthedocs.org/projects/batconf/badge/?version=stable)](https://batconf.readthedocs.io/en/stable/)
[![Python](https://img.shields.io/pypi/pyversions/batconf)](https://pypi.org/pypi/batconf/)
[![Tidelift](https://tidelift.com/badges/package/pypi/batconf)](https://tidelift.com/subscription/pkg/pypi-batconf)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/lundybernard/batconf/badge)](https://securityscorecards.dev/viewer/?uri=github.com/lundybernard/batconf)


Compose structured hierarchical configurations from multiple sources.
Enable your code to adapt seamlessly to the current context.
Allow users in different contexts to use the config source that works best for
them.

* Hierarchical priority: CLI > Environment > config file > module defaults
* Provides builtin support for common config sources:
    * CLI args
    * Environment Variables
    * Config files: `ini`, `toml` and `yaml`
    * Config classes with default values
* Customizable priority: the `SourceList` sets the lookup order, and you can change it
* Easily extendable, add new sources to serve your needs.
* Set reasonable defaults, and override them as needed.
* Designed for 12-factor applications (config via Environment Variables)
* `ConfigSingleton`: share a single `Configuration` instance across your application
* `insert_source`: dynamically add configuration sources at runtime
* Subscript access: `cfg['key']` as an alternative to `cfg.key`, enabling dynamic lookups like `cfg.clients[client_id]`
* `BatconfError`: catch every configuration failure with one `except` clause

Users can create their own config sources
by creating classes that satisfy `batconf.sources.types.SourceInterfaceP`.
See the [custom source guide](https://batconf.readthedocs.io/en/stable/guide.html)
for a walk-through.

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

## How BatConf Compares

| Tool | Layered sources | Config object access | Validation | CLI integration |
|---|---|---|---|---|
| **BatConf** | CLI / env / files / dataclass defaults | dot-path + subscript | bring your own (by design) | explicit — your app owns its argparse parser |
| pydantic-settings | env / files / secrets / CLI | typed model attributes | built-in (pydantic) | generated parser |
| environs | env vars only | none (per-value reads) | built-in (marshmallow) | none |
| python-decouple | env / `.ini` / `.env` | none (per-value reads) | `cast` callable only | none |
| Dynaconf | many formats + env profiles | dot-path + subscript | built-in validators | management CLI |
| python-dotenv | `.env` loader only | plain dict | none | none |
| Hydra / OmegaConf | YAML composition + CLI overrides | dot-path + subscript | opt-in structured configs | framework owns `argv` |
| configparser (stdlib) | INI files | subscript (strings) | none | none |

See the full
[comparison guide](https://batconf.readthedocs.io/en/latest/comparison.html)
for details, access-interface ergonomics, and guidance on choosing a tool.

## Professional Support

![Tidelift Logo](docs/source/_static/Tidelift_Logos_RGB_Tidelift_Mark_On-White.png)
BatConf participates in the Tidelift open source sustainability program.
Organizations can support the ongoing maintenance of BatConf
while receiving professional assurances through a Tidelift subscription.

Professionally supported BatConf is now available.

Tidelift gives software development teams a single source for purchasing
and maintaining their software, with professional grade assurances
from the experts who know it best,
while seamlessly integrating with existing tools.

[Get supported BatConf with the Tidelift subscription](
https://tidelift.com/subscription/pkg/pypi-batconf?utm_source=pypi-batconf&utm_medium=readme
)

## [Example Configuration](tests/example/)
Check out our [Quick Start Guide](https://batconf.readthedocs.io/en/stable/quickstart.html)

and the example project in [tests/example/](/tests/example)
which includes tests and documentation.

### Quick Example

```python
from dataclasses import dataclass
from batconf import (
    ConfigSingleton,
    insert_source,
    Configuration,
    SourceList,
    EnvSource,
    IniSource,
    NamespaceSource,
    Namespace,
)

@dataclass
class AppConfig:
    host: str = 'localhost'
    port: str = '8080'

def get_config() -> Configuration:
    sources = SourceList([EnvSource(), IniSource('config.ini')])
    return Configuration(sources, AppConfig, path='app')

# A shared singleton — import CFG anywhere in your application
CFG = ConfigSingleton(get_config)

# Attribute access
host = CFG.host

# Subscript access — useful for dynamic keys
key = 'host'
host = CFG[key]

# Add a source at runtime (e.g. after CLI args are parsed)
args = Namespace()
setattr(args, 'app.host', 'example.com')
insert_source(cfg=CFG, source=NamespaceSource(args))
```


## Install Instructions

Install the core package, which has no dependencies of its own:

`pip install batconf`

Install with Yaml support:

`pip install 'batconf[yaml]'`

Install with Toml support, needed only on python 3.10:

`pip install 'batconf[toml]'`

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


## Stability and Upgrading

BatConf follows Semantic Versioning. The
[stability policy](https://batconf.readthedocs.io/en/stable/stability.html)
states what the 1.0 API freeze covers, how deprecations are announced
before a name is removed, and what BatConf deliberately leaves to you.

Upgrading from a 0.x release? The
[migration guide](https://batconf.readthedocs.io/en/stable/migration.html)
covers every rename and removal.

## Architecture Decision Records

Significant design decisions are documented in
[`docs/decisions/`](docs/decisions/). Start with the
[foundational ADRs](docs/decisions/0000-foundational/) to understand the
core philosophy, then read the per-feature groups for decisions made
during specific refactors.

## Dev Guide

### Install dev dependencies (pytest, mypy, etc)

`pip install --group=dev -e .`


## Security contact information

To report a security vulnerability, please use the
[Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.
