```{currentmodule} batconf
```

```{toctree}
:hidden: true
:maxdepth: 2
```

# Quick Start

## Install

Install with `pip`:

```bash
pip install batconf
```


## Project Setup
BatConf is designed to be minimally invasive.  Most projects only need a single
file which imports from batconf.  Config classes are stdlib 
[dataclasses](https://docs.python.org/3/library/dataclasses.html) 
which can be used with or without BatConf.

1. Add a {ref}`GlobalConfig` dataclass to your module's root `__init__.py`
   * The Config dataclasses provide basic config objects for your classes and 
      modules.
   * Config dataclasses can be nested to create a configuration tree structure.
2. Add the {ref}`get_config` function to `{yourmodule}/conf.py`
   * This is where we create the list of config sources which we will use to
      lookup values. 
3. Use {ref}`get_config` to get the global, or partial config you need to
   run your code.


### References
* [Example Configuration](
https://github.com/lundybernard/batconf/tree/main/tests/example
) (tests/example/project/):
the example python module "project" uses BatConf. Test cases are included 
which show specific uses with more context.
* [template project example](
https://github.com/lundybernard/project_template/blob/main/bat/conf.py
): 
Is a project template with a basic batconf setup


(GlobalConfig)=
### GlobalConfig and Config classes
The `GlobalConfig` class is a python `dataclass`, used for namespacing
and providing a structured configuration tree.
* Its attributes should be other Config dataclasses for sub-modules.
* It can define config options, and they can be given default values.


```python
# yourmodule/__init__.py
from dataclasses import dataclass
from .example import Config


@dataclass
class GlobalConfig:
    # example module with configuration dataclass
    example: Config
    option: str = "default value"
```

```python
# yourmodule/example/__init__.py
from dataclasses import dataclass
from .client import ClientConfig

@dataclass
class ExampleConfig:
    client: ClientConfig
    moduleoption: str = 'a module level option'
```


(get_config)=
### get_config function
Add a `get_config` function to your project, I recommend putting this in 
{yourmodule}/config.py

Most projects can copy this example with minimal modification.

```python
# {yourmodule}/conf.py
from . import GlobalConfig

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

#### Defaults
The default will construct a :class:`batconf.manager.Configuration` 
object using your {ref}`GlobalConfig`
```python
# yourmodule/lib.py
from .conf import get_config
from .example.client import Client 

def application_code():
    cfg = get_config()
    print(f'default option value: {cfg.option=}')
    client = Client.from_config(cfg.example.client)
    client.do_work()
```


#### Partial Configs
Given any valid `config_class`, get_config will return a Configuration with it
as the root.
```python
from yourmodule.conf import get_config
from yourmodule.client import ClientConfig

cfg = get_config(ClientConfig)
print(cfg.username)
```


## Usage

Access config option values using python's attribute(`.`) notation.
```python
In [1]: cfg = get_config()
WARNING:root:Config File not specified: create config.yaml, set environment variable BAT_CONFIG_FILE to config file path, or speicfy a config file.

In [2]: print(cfg)
Root <class 'bat.GlobalConfig'>:
    |- server = <class 'bat.server.ServerConfiguration'>:
    |    |- host: "0.0.0.0"
    |    |- port: "5000"
SourceList=[
    <batconf.sources.env.EnvConfig object at 0x7faf102ed4f0>,
    <batconf.sources.file.FileConfig object at 0x7faf102e7440>,
]

In [3]: cfg.server.host
Out[3]: '0.0.0.0'
```

### CLI Args
When running commands from a CLI, use the parsed args(`argparse.Namespace`).

```python
yourmodule/clilib.py
from argparse import Namespace
from .conf import get_config
from .example.client import Client

# execute > `yourmodulecli --flag client --address=0.0.0.0 connect`
def cli_client_connect(args: Namespace):
    cfg = get_config(cli_args=args)
    print(f'cli arg "flag": {cfg.flag=}')
    print(f'Connect to server@{cfg.example.client.address}')
    client = Client.from_config(cfg.example.client)
    client.connect()
```
Warning: The builtin `CliArgsConfig` has some sharp edges. 
Additional documentation and development are needed to make it easier to use.

*Gotcha:*
argparse Namespace is a flat structure. In the current implementation this
  results in any arguments from the CLI overwriting all other config options
  with the same name.  In most projects, this kind of namespace collision has
  not caused serious issues, but it is a known defect.  It is possible to use
  nested Namespaces to solve this problem, but it adds complexity and needs to
  be documented.


### Configuration File (YAML)

```yaml
default: dev

dev:
  yourproject:
    example:
      client:
        username: devusr
        password: changeme
        address: 0.0.0.0

prod:
  yourproject:
    example:
      client:
        username: produser
        password: lets-add-a-secure-source-for-this
        address: 192.168.1.1
```
This example has 2 environments, dev and prod, the default environment is set
to dev.
In each environment we have a section for the root module `yourproject`, and
configuration options for the `client` found in `yourproject.example.client`.

#### setting the configuration file
* *Default*: If no config file is specified, batconf will look for a file named 
  `config.yaml` in your working directory.
* *Environment variable*: `BAT_CONFIG_FILE` is an environment variable 
  that you can set to the path to your config file.
* *CLI args*: I recommend adding config file path and environment to your CLI
  for convenience. ex: `> yourcli --config_file=~/mycfg.yaml --env=staging ...`
