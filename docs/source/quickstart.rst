.. currentmodule:: batconf

.. toctree::
   :hidden:
   :maxdepth: 2

Quick Start
===========

Install
-------

Install with ``pip``:

.. code-block:: bash

    pip install batconf


Project Setup
-------------
BatConf is designed to be minimally invasive. Most projects only need a single
file which imports from batconf. Config classes are stdlib
`dataclasses <https://docs.python.org/3/library/dataclasses.html>`_
which can be used with or without BatConf.

1. Add a :ref:`ConfigSchema` dataclass to your module's ``conf.py``

   * The Config dataclasses provide basic config objects
     for your classes and modules.
   * Config dataclasses can be nested to create a configuration schema.

2. Add the :ref:`get_config` function to ``{yourmodule}/conf.py``

   * This is where we create the list of config sources which we will use
     to lookup values.

3. Use :ref:`get_config` to get the global, or partial config
   you need to run your code.


References
~~~~~~~~~~
* `Example Configuration <https://github.com/lundybernard/batconf/tree/main/tests/example>`_
  (tests/example/project/): the example python module "project" uses BatConf.
  Test cases are included which show specific uses with more context.
* `template project example <https://github.com/lundybernard/project_template/blob/main/bat/conf.py>`_:
  Is a project template with a basic batconf setup

.. _ConfigSchema:


ConfigSchema and Config classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``ConfigSchema`` class is a python ``dataclass``, used for namespacing
and providing a structured configuration tree.

* Its attributes should be other Config dataclasses for sub-modules.
* It can define config options, and they can be given default values.

.. code-block:: python
    :caption: yourmodule/conf.py

    from dataclasses import dataclass
    from .example.client import ClientConfig

    @dataclass
    class ExampleConfig:
        client: ClientConfig
        moduleoption: str = 'a module level option'

    @dataclass
    class YourProjectConfigSchema:
        # example module with configuration dataclass
        example: ExampleConfig
        option: str = "default value"


.. _get_config:

get_config function
~~~~~~~~~~~~~~~~~~~
Add a ``get_config`` function to your project, I recommend putting this in
``{yourmodule}/conf.py``

Most projects can copy this example with minimal modification.

.. code-block:: python
    :caption: {yourmodule}/conf.py

    from batconf import Configuration, ConfigProtocol, SourceList
    from batconf.sources.argparse import NamespaceConfig, Namespace
    from batconf.sources.env import EnvConfig
    from batconf.sources.file import FileConfig

    # Default config file path,
    # look for config.ini in the current working directory
    CONFIG_FILE_NAME = str(Path.cwd() / "config.ini")

    @dataclass
    class ConfigSchema:
        opt: str = 'default opt'

    def get_config(
        config_class: ConfigProtocol = ConfigSchema,  # type: ignore
        cfg_path: str = 'yourmodule',
        cli_args: Namespace = None,
        config_file: FileConfig = None,
        config_file_name: str = CONFIG_FILE_NAME,
        config_env: str = None,
    ) -> Configuration:

        # Build a prioritized config source list
        config_sources = [
            NamespaceConfig(cli_args) if cli_args else None,
            EnvConfig(),
            config_file if config_file else IniConfig(
                config_file_name, config_env=config_env
            ),
        ]

        source_list = SourceList(config_sources)
        return Configuration(source_list, config_class, path=cfg_path)


Defaults
^^^^^^^^
The default will construct a :class:`batconf.manager.Configuration` object
using your :ref:`ConfigSchema`

.. code-block:: python
    :caption: yourmodule/lib.py

    from .conf import get_config
    from .example.client import Client

    def application_code():
        cfg = get_config()
        print(f'default option value: {cfg.option=}')
        client = Client.from_config(cfg.example.client)
        client.do_work()


Partial Configs
^^^^^^^^^^^^^
Given any valid ``config_class``, get_config will return a Configuration with it
as the root.

.. code-block:: python

    from yourmodule.conf import get_config
    from yourmodule.client import ClientConfig

    cfg = get_config(ClientConfig, cfg_path='yourmodule.example.client')
    print(cfg.username)


Usage
-----

Access config option values using python's attribute(``.``) notation.

.. code-block:: python

    In [1]: cfg = get_config()

    In [2]: print(cfg)
    yourproject <class 'yourproject.conf.ConfigSchema'>:
        |- server = <class 'yourproject.server.ServerConfiguration'>:
        |    |- host: "0.0.0.0"
        |    |- port: "5000"
    SourceList=[
        <batconf.sources.env.EnvConfig object at 0x7faf102ed4f0>,
        <batconf.sources.ini.IniConfig object at 0x7faf102e7440>,
    ]

    In [3]: cfg.server.host
    Out[3]: '0.0.0.0'


CLI Args
~~~~~~~
When running commands from a CLI, use the parsed args(``argparse.Namespace``).

.. code-block:: python
    :caption: yourmodule/clilib.py

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



Configuration File
~~~~~~~~~~~~~~~~~~
This example has 2 environments, dev and prod, the default environment is set
to dev.
In each environment we have a section for the root module ``yourproject``, and
configuration options for the ``client`` found in ``yourproject.example.client``.


Ini
^^^

.. code-block:: ini
    :caption: config.ini

    [batconf]
    default_env = dev

    [dev]
    [dev.yourproject]
    [dev.yourproject.example]
    [dev.yourproject.example.client]
    username = devusr
    password = changeme
    address = 0.0.0.0

    [prod]
    [prod.yourproject]
    [prod.yourproject.example]
    [prod.yourproject.example.client]
    username = produser
    password = lets-add-a-secure-source-for-this
    address = 192.168.1.1

Yaml
^^^^

.. code-block:: yaml
    :caption: config.yaml

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



Setting the configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Choosing default config file names and locations bears careful consideration,
and we will cover options and best-practices in an advanced usage guide.

The example assumes 'config.ini' is in the current working directory.

* **Default**: If the specified config file is not found,
  the default behavior is to raise a warning.
* **CLI args**: I recommend adding config file path and environment to your CLI
  for convenience. ex: ``> yourcli --config_file=~/mycfg.yaml --env=staging ...``
