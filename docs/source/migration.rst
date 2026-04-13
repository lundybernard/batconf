###############
Migration Guide
###############


******
v0.4.0
******

========================
FileConfig Removed
========================
``batconf.sources.file.FileConfig`` has been removed.
Replace it with :class:`~batconf.sources.ini.IniConfig` or
:class:`~batconf.sources.yaml.YamlConfig` as appropriate.

========================
New Public API
========================
The following names are now importable directly from ``batconf``:

* :class:`~batconf.manager.Configuration`
* :class:`~batconf.source.SourceList`
* :class:`~batconf.lib.ConfigSingleton`
* :func:`~batconf.lib.insert_source`
* ``NamespaceSource``, ``Namespace``
* ``EnvSource``
* ``IniSource``
* ``YamlSource`` (requires ``batconf[yaml]``)

Old submodule imports still work but the top-level names are now preferred:

.. code-block:: python

    # old
    from batconf.sources.argparse import NamespaceConfig, Namespace
    from batconf.sources.env import EnvConfig
    from batconf.sources.ini import IniConfig

    # new
    from batconf import NamespaceSource, Namespace, EnvSource, IniSource

========================
ConfigSingleton
========================
A new :class:`~batconf.lib.ConfigSingleton` class provides a shared,
lazily-initialised configuration instance that can be imported anywhere
in your application. See the :ref:`get_config` section of the quickstart
for usage.

========================
insert_source
========================
:func:`~batconf.lib.insert_source` allows a configuration source to be
added to a running :class:`~batconf.manager.Configuration` or
:class:`~batconf.lib.ConfigSingleton` at runtime. This is the recommended
pattern for injecting CLI args after argument parsing.

========================
Subscript Access
========================
:class:`~batconf.manager.Configuration` now supports subscript notation,
so ``cfg['key']`` is equivalent to ``cfg.key``. This enables dynamic
lookups such as ``cfg.clients[client_id]``.


******
v0.2.0
******
===================
Yaml Optional Extra
===================
pyyaml is no longer a default dependency of BatConf.
It is now available as an optional extra.

If you wish to keep using Yaml format for your configuration,
you should update your dependencies in your `pyproject.toml`

.. code-block:: TOML
    :caption: old pyproject.toml

    dependencies = [
        "batconf[yaml]>=0.2",
    ]

Projects which require yaml for BatConf and for project code
should make both dependencies explicit:

.. code-block:: TOML
    :caption: pyproject.toml

    dependencies = [
        "batconf[yaml]>=0.2",
        "pyyaml=*",
    ]

====================================
TOML Optional Extra for Python<3.11
====================================
Python provides stdlib support for Toml in version 3.11+
(via ``tomllib``). BatConf provides an optional extra ``[toml]``
for Python 3.10 and earlier.

.. code-block:: TOML
    :caption: pyproject.toml

    dependencies = [
        "batconf[toml]>=0.2",
    ]

If your project needs to support multiple versions of python,
both <= 3.10 and >= 3.11, you can do so,
only including the toml dependency when required, like so:

.. code-block:: TOML
    :caption: pyproject.toml

    dependencies = [
        "batconf=*",
        "batconf[toml]>=0.2; python_version <= '3.10'",
    ]


==============================
FreeForm Configuration Schemas
==============================
Previous versions of BatConf inferred the structure of the configuration schema
from the structure of your module's namespace.
That behavior is deprecated, but it still works for now.

Going forward, we recommend defining your Configuration Schema in `conf.py`
or in its own module.

.. code-block:: PYTHON
    :caption: conf.py example Schema

    # Import MyClient, which provides a 'Config' dataclass.
    # Import a configuration schema from a submodule in your project.
    from .submodule import MyClient, SubmoduleConfigSchema


    @dataclass
    class ClientConfigurationsSchema:
        """
        .. versionchanged:: 0.2
           Added support for multiple configurations from single Schema.
        """
        clientA: MyClient.Config
        clientB: MyClient.Config
        doc: str = "Configurations for multiple clients"


    @dataclass
    class ProjectConfigSchema:
        # Configuration subsection for a specific submodule
        submodule: SubmoduleConfigSchema
        clients: ClientConfigurationsSchema
        # Schemas can be reused
        moreclients: ClientConfigurationsSchema
        doc: str = "Root Configuration Schema for your project"

This approach gives us much more flexibility to organize our configurations
to suit our projects.
