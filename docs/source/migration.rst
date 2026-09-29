###############
Migration Guide
###############


****************
v0.5.0 (planned)
****************

BatConf deprecates and documents a name in a patch release (n.n.x) and
removes it in the next minor release (n.x). Every name and default
behaviour in this section still works in v0.4.x and emits a
``DeprecationWarning`` naming v0.5.0.

Upgrade to v0.4.1 first and run your test suite with deprecations
promoted to errors. Each failure points at one line to change:

.. code-block:: shell

    python -m pytest --pythonwarnings error::DeprecationWarning

==================
What is removed
==================

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Removed in v0.5.0
     - Replacement
   * - ``batconf.sources.ini.IniConfig``
     - ``IniSource`` — argument order differs
   * - ``batconf.sources.toml.TomlConfig``
     - ``TomlSource`` — drop-in
   * - ``batconf.sources.yaml.YamlConfig``
     - ``YamlSource`` — constructor and file format differ
   * - ``batconf.sources.env.EnvConfig``
     - ``EnvSource`` — drop-in rename
   * - ``batconf.sources.argparse.NamespaceConfig``
     - ``NamespaceSource`` — drop-in rename
   * - ``batconf.sources.args.CliArgsConfig``, and the whole
       ``batconf.sources.args`` module
     - ``NamespaceSource`` — different lookup rule
   * - ``batconf.sources.dataclass.DataclassConfig``
     - none; delete the source-list entry
   * - ``batconf.source.SourceInterface``
     - ``SourceInterfaceP``, or no base class at all
   * - The ``module=`` keyword of ``.get()`` on every
       ``SourceInterfaceP`` source, and of ``EnvSource.env_name()``
     - ``path=``
   * - ``Protocol``- and ``Proto``-suffixed aliases in
       ``batconf.types``
     - the ``P``-suffixed names
   * - The module-name default of the ``path`` parameter of
       ``Configuration``
     - an explicit ``path=``, or the root
   * - The hardcoded ``BAT`` prefix of ``EnvSource``
     - ``EnvSource(prefix=...)``

===========================
The shared source interface
===========================
The removals above follow from one change: the source classes now share
one interface and one constructor. Every source implements
:py:class:`SourceInterfaceP <batconf.sources.types.SourceInterfaceP>`,
whose method is ``get(key, path)``. Every file source also implements
:py:class:`FileSourceP <batconf.sources.types.FileSourceP>`, whose
constructor is:

.. code-block:: python

    Source(
        file_path,
        file_format='environments',
        config_env=None,
        missing_file_option='warn',
    )

The sections below cover every entry that is not a plain rename.

==================
IniConfig
==================
``IniSource`` reordered the parameters after ``file_path``, so a
positional second argument changes meaning:

.. code-block:: python

    # old
    from batconf.sources.ini import IniConfig

    source = IniConfig('config.ini', 'dev')

    # new — 'dev' would be read as file_format and raise
    # ValueError: Invalid file_format: dev
    from batconf import IniSource

    source = IniSource('config.ini', config_env='dev')

==================
YamlConfig
==================
``YamlSource`` renamed the constructor keyword, so the obvious swap
raises ``TypeError: unexpected keyword argument 'config_file_name'``:

.. code-block:: python

    # old
    from batconf.sources.yaml import YamlConfig

    source = YamlConfig(config_file_name='config.yaml')

    # new
    from batconf import YamlSource

    source = YamlSource(file_path='config.yaml')

``enable_config_environments=False`` has no direct counterpart; use
``file_format='sections'``. ``.get()`` takes ``path=`` where
``YamlConfig.get()`` took ``module=``.

``YamlConfig`` read the active environment from the file's top-level
``default`` key. ``YamlSource`` reads ``batconf.default_env``, so the
file itself needs updating:

.. code-block:: yaml
    :caption: config.yaml

    # old
    default: dev

    # new
    batconf:
      default_env: dev

    dev:
      yourproject:
        client:
          api_key: example_api_key

==================
CliArgsConfig
==================
``NamespaceSource`` is the replacement, but the two resolve keys
differently — this is a behaviour change, not a rename.

``CliArgsConfig`` ignored the config path and matched on the final key
segment alone, so a single ``--key1`` set ``project.key1``,
``project.submodule.key1`` and every other path ending in ``key1``.
``NamespaceSource`` looks up the full dotted ``path.key`` string on the
namespace, so each value reaches exactly one config path.

Give each argument a ``dest=`` holding its full dotted path:

.. code-block:: python

    # old
    from batconf.sources.args import CliArgsConfig

    parser.add_argument('--key1')
    source = CliArgsConfig(parser.parse_args())

    # new
    from batconf import NamespaceSource

    parser.add_argument('--key1', dest='project.submodule.key1')
    source = NamespaceSource(parser.parse_args())

``NamespaceSource`` does not fall back to a bare key, and nested
namespaces never resolve.

==================
DataclassConfig
==================
This source has nothing to replace it.
:class:`~batconf.manager.Configuration` has read default values from the
config schema itself since v0.2.0, so the source only repeated what the
schema already provided. Delete the entry from your source list:

.. code-block:: python

    # old
    from batconf.sources.dataclass import DataclassConfig

    sources = SourceList([
        NamespaceSource(args),
        EnvSource(),
        DataclassConfig(ProjectConfigSchema),
    ])

    # new
    sources = SourceList([
        NamespaceSource(args),
        EnvSource(),
    ])

==================
SourceInterface
==================
Custom sources do not need a base class: any object with a conforming
``get`` method is a valid source. Subclass
:py:class:`SourceInterfaceP <batconf.sources.types.SourceInterfaceP>` if
you want a type checker to flag an incomplete implementation.

.. code-block:: python

    # old
    from batconf.source import SourceInterface

    class VaultSource(SourceInterface):
        ...

    # new
    from batconf.sources.types import SourceInterfaceP

    class VaultSource(SourceInterfaceP):
        ...

``isinstance`` checks against ``SourceInterface`` move to
``SourceInterfaceP``, which is runtime-checkable.

==================
The module keyword
==================
Every source implements
:py:class:`SourceInterfaceP <batconf.sources.types.SourceInterfaceP>`,
whose method is ``get(key, path)``. ``.get(module=)`` becomes
``.get(path=)`` on every source that still accepts the old keyword:

.. code-block:: python

    # old
    EnvSource().get('api_key', module='project.client')

    # new
    EnvSource().get('api_key', path='project.client')

``EnvSource.env_name()`` also accepts ``module=``. It is deprecated in
v0.4.x and removed in v0.5.0. Its second parameter is ``path``:

.. code-block:: python

    # old
    EnvSource().env_name('api_key', module='project.client')

    # new
    EnvSource().env_name('api_key', path='project.client')

==================
Type aliases
==================
The ``Protocol``- and ``Proto``-suffixed aliases in
:mod:`batconf.types` are removed. Use the ``P``-suffixed names:
``ConfigP``, ``FieldP``, ``SourceInterfaceP``, ``SourceListP``.

==================
The module path
==================
A :class:`~batconf.manager.Configuration` built without ``path`` took
the Python module name of its schema class as the namespace for every
lookup. An absent or empty path now mounts the schema at the root.

Pass the module name as ``path=`` to keep every lookup as it was. This
is the smallest change, and it renames nothing in your config file or
your environment:

.. code-block:: python

    # old — the namespace is 'yourproject.conf', the schema's module
    cfg = Configuration(source_list, ProjectConfigSchema)

    # new
    cfg = Configuration(
        source_list,
        ProjectConfigSchema,
        path='yourproject.conf',
    )

Choose your own namespace instead, or mount at the root. The call site
is unchanged for the root, so the file moves rather than the code:

.. code-block:: ini
    :caption: config.ini (file_format='sections')

    # old
    [yourproject.conf.server]
    host = localhost

    # new
    [server]
    host = localhost

A sub-configuration mounts under its field name alone, so
``cfg.server.host`` reads ``server.host``. A key declared on the root
schema has no section name left in an INI file, and INI has no unnamed
section. The ``[/ROOT/]`` section holds those keys from v0.4.x, in the
``sections`` layout and in the ``flat`` layout; see ADR 0019.

The ``flat`` layout keeps its keys at the top of the file, with no
section header. The loader adds its own ``root`` section before it
parses the file, so a file that spells a ``[root]`` header fails with
``configparser.DuplicateSectionError``. That header is an error, not a
deprecated spelling. A flat file does not need a change.

==================
The BAT prefix
==================
``EnvSource`` prefixed a variable name with ``BAT`` when the path was
empty, and prefixed nothing otherwise. The namespace now comes from
``prefix``, and it leads every name:

.. code-block:: python

    # old — BAT_API_KEY, and only when no path was given
    EnvSource().get('api_key')

    # new — YOURPROJECT_API_KEY, with or without a path
    EnvSource(prefix='yourproject').get('api_key')

A :class:`~batconf.manager.Configuration` always supplied a path before
v0.5.0, so a source behind one never reached the ``BAT`` branch. Keep
``path=`` and declare no prefix, and every variable name stays as it
was: path ``yourproject.conf.server`` and key ``host`` read
``YOURPROJECT_CONF_SERVER_HOST`` in both releases.

.. warning::

   ``prefix='BAT'`` does not restore the old rule. The old prefix
   applied at the root only; a declared prefix applies everywhere, so
   path ``server`` and key ``host`` move from ``SERVER_HOST`` to
   ``BAT_SERVER_HOST``.

In v0.4.x, ``prefix=None`` reads a bare uppercase name at the root, so a
schema field named ``path`` or ``user`` resolves against an ambient
process variable. ADR 0018 proposes to refuse bare names at the root in
v0.5.0. Declare a prefix to keep every lookup inside a namespace under
either rule.

``BATCONF_`` is reserved for BatConf's own variables. Do not choose it
as your prefix.


******
v0.4.0
******

========================
FileConfig Removed
========================
``batconf.sources.file.FileConfig`` has been removed. It read YAML files
only, so its replacement is :class:`~batconf.sources.yaml.YamlSource`.
The constructor keyword ``config_file_name`` was renamed to ``file_path``,
so the obvious swap raises
``TypeError: unexpected keyword argument 'config_file_name'``:

.. code-block:: python

    # old
    from batconf.sources.file import FileConfig

    source = FileConfig(config_file_name='config.yaml')

    # new
    from batconf import YamlSource

    source = YamlSource(file_path='config.yaml')

``FileConfig`` selected the active environment from the file's top-level
``default`` key. ``YamlSource`` defaults to ``file_format='environments'``,
which reads it from ``batconf.default_env`` instead, so the file itself
needs updating:

.. code-block:: yaml
    :caption: config.yaml

    # old
    default: dev

    # new
    batconf:
      default_env: dev

    dev:
      yourproject:
        client:
          api_key: example_api_key

``FileConfig.get()`` took a ``module`` keyword; ``YamlSource.get()`` takes
``path``.

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
* ``TomlSource``
* ``YamlSource`` (requires ``batconf[yaml]``)

Old submodule imports still work but the top-level names are now preferred:

.. code-block:: python

    # old
    from batconf.sources.argparse import NamespaceConfig, Namespace
    from batconf.sources.env import EnvConfig

    # new
    from batconf import NamespaceSource, Namespace, EnvSource

``IniConfig``, ``TomlConfig`` and ``YamlConfig`` still import too, but they
are deprecated and emit a ``DeprecationWarning`` on import — see
`Deprecations`_ below for their replacements.

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

========================
Deprecations
========================
The following names still work but now emit a ``DeprecationWarning`` and
will be removed in v0.5.0. Update your imports:

.. code-block:: python

    # old                              # new
    from batconf.sources.ini import IniConfig    # IniSource
    from batconf.sources.toml import TomlConfig  # TomlSource
    from batconf.sources.yaml import YamlConfig  # YamlSource
    from batconf.sources.args import CliArgsConfig  # NamespaceSource

The ``module`` keyword argument to ``.get()`` is also deprecated, on
``EnvSource``, ``NamespaceSource`` and
``batconf.sources.dataclass.DataclassConfig``. It will be removed in
v0.5.0; use ``path`` instead:

.. code-block:: python

    # old
    EnvSource().get('api_key', module='project.client')

    # new
    EnvSource().get('api_key', path='project.client')

The file sources ``IniSource``, ``TomlSource`` and ``YamlSource`` accept
``path`` only and raise ``TypeError`` if given ``module``.

The ``Protocol``- and ``Proto``-suffixed type names were removed outright
from the modules that used to export them, so update those imports:

.. code-block:: python

    # old — each of these now raises ImportError
    from batconf.manager import ConfigProtocol, FieldProtocol
    from batconf.source import SourceInterfaceProto
    from batconf.sources.dataclass import ConfigProtocol, FieldProtocol

    # new
    from batconf.types import ConfigP, FieldP, SourceInterfaceP

:mod:`batconf.types` is the one place the old names still resolve, and
they emit a ``DeprecationWarning`` when they do. The full mapping, from
the removed name to its ``batconf.types`` alias to the ``P``-suffixed name
to prefer:

* ``batconf.manager.ConfigProtocol``,
  ``batconf.sources.dataclass.ConfigProtocol``
  → ``batconf.types.ConfigProtocol`` → ``batconf.types.ConfigP``
* ``batconf.manager.FieldProtocol``,
  ``batconf.sources.dataclass.FieldProtocol``
  → ``batconf.types.FieldProtocol`` → ``batconf.types.FieldP``
* ``batconf.source.SourceInterfaceProto``
  → ``batconf.types.SourceInterfaceProto``
  → ``batconf.types.SourceInterfaceP``
* ``SourceListProto`` (new in 0.4.0, ``batconf.types`` only)
  → ``batconf.types.SourceListP``


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
