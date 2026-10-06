=========
Changelog
=========

This is a record of BatConf releases and what went into them,
in reverse chronological order.
All previous releases should still be available
:pypi:`on PyPI <batconf>`.


BatConf 1.x
==============

.. _v1.0.0:

------------------
1.0.0 - 2026-08-30
------------------

The API freeze. BatConf follows Semantic Versioning from here, under a
published :doc:`stability` policy that states what the freeze covers,
how a name is deprecated before it is removed, and what BatConf leaves
to your application.

Upgrading from 0.5.0 needs no code changes, unless you build a file
source with ``missing_file_option='error'``.

Added:

* An error hierarchy. Every failure BatConf raises now carries a
  BatConf type, so one ``except``
  :class:`~batconf.errors.BatconfError` clause covers configuration
  failures and separates them from your application's own. The
  concrete errors are :class:`~batconf.errors.ConfigFileNotFound`,
  :class:`~batconf.errors.ConfigEnvironmentNotFound`,
  :class:`~batconf.errors.ConfigValueNotFound`,
  :class:`~batconf.errors.InvalidFileFormat` and
  :class:`~batconf.errors.SourceDependencyNotFound`; all are exported
  from ``batconf``. Each keeps the standard exception it replaces as a
  second base, so existing ``except ValueError``,
  ``except AttributeError``, ``except FileNotFoundError`` and
  ``except ImportError`` clauses catch exactly as before. See ADR 0022.
* A :doc:`stability` page: the versioning scheme, the API surface the
  1.0 freeze covers, the deprecation cycle, and the non-goals.
* An ``AUTHORS`` file naming the people who have contributed.

Changed:

* A file source built with ``missing_file_option='error'`` and a
  missing file raises
  :class:`~batconf.errors.ConfigFileNotFound` at construction. It
  previously failed at the first ``.get()``, inside a lazy property,
  so a program given a bad config path started normally and failed
  later with nothing to connect the failure to the path. Sources built
  with ``'warn'`` or ``'ignore'`` are unchanged and still read the
  file lazily.
* The ``Development Status`` classifier is now
  ``5 - Production/Stable``.

Fixed:

* A config file lost between building a source and the first read is
  reported as :class:`~batconf.errors.ConfigFileNotFound`. Every source
  previously let the operating system's ``FileNotFoundError`` through
  on that path, so ``except BatconfError`` did not catch it.

Typing:

* :class:`~batconf.manager.Configuration` declares ``config_class`` as
  ``ConfigP`` instead of ``ConfigP | Any``. ``ConfigP`` could not be
  satisfied by any dataclass before — its ``__dataclass_fields__``
  member was invariant — so the ``Any`` carried every call and the
  Protocol checked nothing. ``ConfigP`` and ``FieldP`` now describe
  what a dataclass schema actually provides, and a wrong
  ``config_class`` is a type error at the call site.
* ``ConfigSingleton.__getattr__`` is annotated.
* The ``# type: ignore`` comments deferred to "the next MyPy release"
  are gone, along with the untyped ``_config_env`` properties that
  needed them.

Removed:

* Internal names that nothing referenced: ``ConfigRet``,
  ``EmptyConfigurationSentinel``, ``ConfigParserP``,
  ``_file_loader_map``, ``IniSource._loader`` and the private
  ``_MissingFileOption`` alias. All were private or unused; no
  supported API changes.

Documentation:

* The source lookup rules are stated in the guide: how
  :class:`~batconf.sources.argparse.NamespaceSource` resolves a dotted
  ``dest``, and how :class:`~batconf.sources.env.EnvSource` derives an
  environment variable name.
* A config file contract section covers the three file layouts, the
  reserved ``batconf.default_env`` key, and the string-value rule —
  including two places where the sources differ.
* A walk-through for writing a custom source against
  :py:class:`SourceInterfaceP <batconf.sources.types.SourceInterfaceP>`.
* A flat, non-nested configuration example.
* Quickstart states that schema defaults must be strings, and carries
  the ``[toml]`` extra caveat for Python 3.10.
* The documentation build instructions use the ``docs`` dependency
  group instead of the retired ``.[docs]`` extra.


BatConf 0.x
==============

.. _v0.5.0:

------------------
0.5.0 - 2026-08-29
------------------

The removal release for everything deprecated in 0.4.x. Every name and
default behaviour below warned in v0.4.1 and named v0.5.0 as its removal
version. Upgrade to v0.4.1 first and run your test suite with
deprecations promoted to errors; each failure points at one line to
change. See :doc:`migration`.

Two derived namespaces go with this release: the module name a schema
took as its config path, and the ``BAT`` prefix a root-level environment
lookup took. A namespace is now something the caller declares, or the
root.

Breaking changes:

* The legacy file source classes ``IniConfig``, ``TomlConfig`` and
  ``YamlConfig`` are removed. Use
  :class:`~batconf.sources.ini.IniSource`,
  :class:`~batconf.sources.toml.TomlSource` and
  :class:`~batconf.sources.yaml.YamlSource`. Only ``TomlSource`` is a
  drop-in: ``IniSource`` reorders the arguments after ``file_path``, and
  ``YamlSource`` renames ``config_file_name`` to ``file_path`` and reads
  the active environment from ``batconf.default_env``.
* ``CliArgsConfig`` and the whole ``batconf.sources.args`` module are
  removed. :class:`~batconf.sources.argparse.NamespaceSource` replaces
  it, and resolves the full dotted path rather than the last key
  segment, so each argument needs a ``dest=`` holding its config path.
* ``DataclassConfig`` and the whole ``batconf.sources.dataclass`` module
  are removed. There is no replacement:
  :class:`~batconf.manager.Configuration` has read schema defaults
  itself since v0.2.0, so the source-list entry is deleted.
* ``EnvConfig`` and ``NamespaceConfig`` are removed. Both were aliases;
  import :class:`~batconf.sources.env.EnvSource` and
  :class:`~batconf.sources.argparse.NamespaceSource`, or take them from
  ``batconf``.
* ``batconf.source.SourceInterface`` is removed.
  :class:`~batconf.sources.types.SourceInterfaceP` is the sole source
  extension point; a custom source needs no base class. ``isinstance``
  checks move to the Protocol, which is runtime-checkable. See ADR 0015.
* The ``module`` keyword argument to ``.get()`` and to
  ``EnvSource.env_name()`` is removed. Every source now takes
  ``get(key, path=None)``, and ``env_name()`` takes ``path``.
* The ``Protocol``- and ``Proto``-suffixed aliases are removed from
  :mod:`batconf.types` and :mod:`batconf.sources.types`. Use
  ``ConfigP``, ``FieldP``, ``SourceInterfaceP`` and ``SourceListP``.
* The module-name config path is removed. An absent or empty ``path``
  mounts the schema at the root of the namespace, and each
  sub-configuration mounts under its field name. A configuration that
  relied on the module name must pass ``path=`` to keep it. See
  ADR 0017.
* The hardcoded ``BAT`` environment prefix is removed.
  :class:`~batconf.sources.env.EnvSource` takes ``prefix``, and the
  prefix leads every variable name rather than standing in at the root.
  See ADR 0018.
* With no prefix and an empty path,
  :class:`~batconf.sources.env.EnvSource` returns ``None`` rather than
  reading a bare uppercase name. A field named ``path`` or ``user`` can
  no longer resolve to an ambient process variable.
  ``EnvSource(raw=True)`` is the opt-in for bare-name resolution.

Added:

* Several top-level schemas hang under one configuration. The parent is
  a :class:`~batconf.manager.Configuration` with no path, so no reserved
  name and no synthetic level appears in the file or the environment
  (#150).
* :class:`~batconf.sources.ini.IniSource` reads the ``[/ROOT/]`` section
  for a key at the root of a schema. ``configparser`` has no unnamed
  section, so INI alone could not express a schema that TOML and YAML
  express. The section is format parity and is not recommended. See
  ADR 0019.

Fixed:

* The missing-value message built an environment variable name by hand,
  including a leading separator at the root, and named a variable no
  prefix could match. It now names the suffix and defers the prefix to
  the source. The tree header drops the path at the root for the same
  reason.
* ``TomlSource.get`` and ``YamlSource.get`` no longer log a warning when
  the dotted lookup runs past a leaf or into an absent section. A key
  miss is ordinary — :class:`~batconf.source.SourceList` moves on to the
  next source — so both return ``None`` silently, matching
  ``IniSource``. The missing-config-file warning is unchanged.

Documentation:

* The first-wins rule is stated as first *truthy* value, in the
  ``SourceList.get`` docstring and in the foundational ADR. Behaviour is
  unchanged: a falsey value is treated as missing.
* ``BATCONF_*`` is reserved for BatConf's own variables, and
  ``BATCONF_ENVIRONMENT`` is the canonical shell-level environment
  selector. No source reads it. The :doc:`guide` documents the two-stage
  bootstrap that does, and the precedence order: ``config_env=``, then
  ``BATCONF_ENVIRONMENT``, then the file's ``default_env``. See
  ADR 0020.
* The :doc:`guide` states what each format can express: only
  ``environments`` holds several environments, ``sections`` holds several
  projects for one environment, ``flat`` is single-tenant, and
  environment variables carry no environment. In a shared file or process
  environment every project declares its own ``path`` and prefix; the
  root belongs to no one. See ADR 0021.


.. _v0.4.1:

------------------
0.4.1 - 2026-08-29
------------------

A deprecation-completeness release. This release removes nothing, and
nothing supported breaks. Every name v0.5.0 removes now warns, names
v0.5.0, and has a :doc:`migration` entry.

Two default behaviours are deprecated alongside the names: the module-name
config path and the ``BAT`` environment prefix. Each derives a namespace
the caller never chose. A namespace the caller declares replaces both.
Both are removed in v0.5.0.

BatConf deprecates and documents a name in a patch release (n.n.x) and
removes it in the next minor release (n.x).

Added:

* :class:`~batconf.sources.env.EnvSource` takes ``prefix``. The prefix
  leads every variable name, so a project namespaces its whole tree:
  ``EnvSource(prefix='mytool')`` reads ``MYTOOL_SERVER_HOST`` for key
  ``host`` at path ``server``. ``prefix=None`` declares no namespace. The
  ``BATCONF_`` namespace is reserved for BatConf's own variables; do not
  choose it.

Deprecated:

* The module-name config path. A
  :class:`~batconf.manager.Configuration` built without ``path`` takes the
  Python module name of its schema class, so a config file must name its
  top section after a module and moving that module breaks a working
  file. Pass ``path=`` to keep the namespace. From v0.5.0 an absent path
  mounts the schema at the root. See ADR 0017.
* The hardcoded ``BAT`` environment prefix. It applies only when the path
  is empty, so it namespaces nothing below the root, and it puts a
  framework name in every user's environment. ``prefix='BAT'`` does not
  restore it: a declared prefix leads every variable name, not the root
  alone. Pass ``prefix=None`` for no prefix, or a namespace of your own;
  the :doc:`migration` guide gives the names each choice produces. See
  ADR 0018.
* ``EnvConfig`` and ``NamespaceConfig`` — the class definitions are
  renamed to :class:`~batconf.sources.env.EnvSource` and
  :class:`~batconf.sources.argparse.NamespaceSource`. The old names still
  import, now through a warning shim. Previously they were the real class
  names, aliased silently, so ``repr`` reported the old name and the
  submodule imports warned nowhere.
* :class:`~batconf.sources.dataclass.DataclassConfig` — obsolete since
  v0.2.0, when :class:`~batconf.manager.Configuration` began reading
  schema defaults itself. There is no replacement: delete the entry from
  your source list.
* ``batconf.source.SourceInterface`` — the abstract base class was a
  workaround for type-checker limitations that no longer reproduce. Custom
  sources do not need a base class; subclass
  :class:`~batconf.sources.types.SourceInterfaceP` for type-checker
  enforcement. See ADR 0015.
* ``CliArgsConfig`` now warns when the name is imported rather than when
  it is instantiated, matching the other deprecated sources. The old
  warning fired late and the default once-per-location filter hid it.
* The ``module`` keyword argument to ``EnvSource.env_name()``. ``.get()``
  deprecated it in v0.4.0 and ``env_name()`` took it without a warning.
  Use ``path``; both are removed in v0.5.0.

Changed:

* Every deprecation warning names v0.5.0 as its removal version. This
  covers the ``IniConfig``, ``TomlConfig`` and ``YamlConfig`` shims and
  the ``Protocol``- and ``Proto``-suffixed aliases in
  :mod:`batconf.types`, none of which named one before.
* ``CliArgsConfig`` pointed users at ``NamespaceConfig from
  batconf.sources.argparse``, contradicting the README and the migration
  guide. The replacement is ``NamespaceSource``, exported from
  ``batconf``.
* The test suite fails on any ``DeprecationWarning``, so a deprecation
  cannot regress to the wrong warning category unnoticed.

Fixed:

* :class:`~batconf.sources.types.SourceInterfaceP` and
  :class:`~batconf.sources.types.FileSourceP` are ``runtime_checkable``,
  so ``isinstance`` and ``issubclass`` accept them instead of raising
  ``TypeError``. Sources migrating off the deprecated ``SourceInterface``
  ABC need this, since the ABC answered ``isinstance``.
* The PyYAML import error ran two sentences together and named the
  deprecated ``YamlConfig``; the missing-YAML-file error ran two
  sentences together; the TOML import error broke a sentence mid-way.

Documentation:

* :doc:`migration` covers the full 0.4 to 0.5 upgrade, one entry per
  removed name. ``IniSource``, ``YamlSource`` and ``NamespaceSource`` are
  not drop-in replacements and get worked examples.
* The user guide and introduction teach ``SourceInterfaceP`` as the
  extension point.


.. _v0.4.0:

------------------
0.4.0 - 2026-08-08
------------------

Breaking changes:

* Remove ``batconf.sources.file.FileConfig`` (deprecated since 0.2.0).
  ``FileConfig`` read YAML files only, so its replacement is
  :class:`~batconf.sources.yaml.YamlSource`. The constructor keyword was
  renamed: ``config_file_name=`` is now ``file_path=``. See the
  :doc:`migration` guide.
* The ``Proto``-suffixed type names (``ConfigProtocol``, ``FieldProtocol``
  and ``SourceInterfaceProto``) have been **removed** from
  :mod:`batconf.manager`, :mod:`batconf.source` and
  :mod:`batconf.sources.dataclass` — importing them from those modules
  raises ``ImportError``. Deprecated equivalents (including the new
  ``SourceListProto``) live in :mod:`batconf.types`. See the
  :doc:`migration` guide.
* :class:`~batconf.source.SourceList` no longer subclasses
  ``SourceInterface``, so ``isinstance``/``issubclass`` checks against
  ``SourceInterface`` no longer match it; use
  :class:`~batconf.types.SourceListP` for type annotations.

Features:

* :class:`~batconf.lib.ConfigSingleton`: global singleton proxy for sharing
  a :class:`~batconf.manager.Configuration` instance across an application
* :func:`~batconf.lib.insert_source`: add a configuration source to a running
  ``Configuration`` or ``ConfigSingleton`` at runtime
* Subscript access on :class:`~batconf.manager.Configuration`:
  ``cfg['key']`` is equivalent to ``cfg.key``
* :class:`~batconf.sources.ini.IniSource` — standardised INI file source
  implementing :class:`~batconf.sources.types.FileSourceP`; the successor to
  :class:`~batconf.sources.ini.IniConfig`. It is **not** a drop-in rename:
  the parameters after ``file_path`` were reordered —
  ``IniConfig(file_path, config_env, missing_file_option, file_format)``
  became
  ``IniSource(file_path, file_format, config_env, missing_file_option)`` —
  so ``IniSource('cfg.ini', 'dev')`` raises
  ``ValueError: Invalid file_format: dev``. Pass ``config_env=`` by keyword.
* :class:`~batconf.sources.toml.TomlSource` — standardised TOML file source
  implementing :class:`~batconf.sources.types.FileSourceP`; the successor to
  :class:`~batconf.sources.toml.TomlConfig`, whose constructor signature it
  keeps unchanged
* :class:`~batconf.sources.yaml.YamlSource` — standardised YAML file source
  implementing :class:`~batconf.sources.types.FileSourceP`; the successor to
  :class:`~batconf.sources.yaml.YamlConfig`. It is **not** a drop-in rename:
  ``config_file_name=`` became ``file_path=`` (the old keyword raises
  ``TypeError``), ``enable_config_environments=False`` has no direct
  counterpart and maps to ``file_format='sections'``, and ``.get()`` takes
  ``path=`` where ``YamlConfig.get()`` took ``module=``
* New top-level public API — ``Configuration``, ``ConfigSingleton``,
  ``SourceList``, ``insert_source``, ``NamespaceSource``, ``Namespace``,
  ``EnvSource``, ``IniSource``, ``TomlSource`` and ``YamlSource`` are now
  importable directly from ``batconf``

Deprecated:

* :class:`~batconf.sources.ini.IniConfig` — use
  :class:`~batconf.sources.ini.IniSource` instead
* :class:`~batconf.sources.toml.TomlConfig` — use
  :class:`~batconf.sources.toml.TomlSource` instead
* :class:`~batconf.sources.yaml.YamlConfig` — use
  :class:`~batconf.sources.yaml.YamlSource` instead
* ``CliArgsConfig`` — use
  :class:`~batconf.sources.argparse.NamespaceConfig` (exported as
  ``NamespaceSource``) instead
* The ``module`` keyword argument to ``.get()`` is deprecated on
  :class:`~batconf.sources.env.EnvConfig` (exported as ``EnvSource``),
  :class:`~batconf.sources.argparse.NamespaceConfig` (exported as
  ``NamespaceSource``) and
  :class:`~batconf.sources.dataclass.DataclassConfig`; use ``path``
  instead. It will be removed in v0.5.0. The new file sources
  (``IniSource``, ``TomlSource``, ``YamlSource``) accept ``path`` only and
  raise ``TypeError`` if given ``module``.
* The ``Proto``-suffixed aliases in :mod:`batconf.types` emit a
  ``DeprecationWarning``; use the ``P``-suffixed names. Everywhere else
  these names were removed outright — see Breaking changes above.


.. _v0.3.1:

------------------
0.3.1 - 2025-11-13
------------------

Bug Fixes:

* Fix Python version shields in readme and pypi
* Update supported version classifiers

Project management:

* Add release issue template


.. _v0.3.0:

------------------
0.3.0 - 2025-10-30
------------------

Supported versions:

* Drop support for python 3.9
* Add support for python 3.13t
* Add support for python 3.14 and 3.14t

Features:

* Support for free-threading/nogil


.. _v0.2.1:

------------------
0.2.1 - 2025-09-18
------------------

Project maintenance

* Updated links on docs page
* Updated example code in readme
* Changed build backend to Hatchling



.. _v0.2.0:

------------------
0.2.0 - 2025-07-07
------------------

Supported versions:

* Drop support for python 3.8
* Add support for python 3.13

Documentation:

* Extensive additions and improvements
* Update `Example Project <https://github.com/lundybernard/batconf/tree/main/tests/example>`_
* Add `Legacy Example <https://github.com/lundybernard/batconf/tree/main/tests/example-legacy>`_
* Add dynamic copyright year (thanks @jgafnea)
* Add spiffy config composition diagram

Code:

* Freeform Schemas: Config schemas no longer depend on module names.
* Add :py:class:`YamlConfig <batconf.sources.yaml.YamlConfig>` to replace
  :py:class:`FileConfig <batconf.sources.file.FileConfig>`

  * Deprecate `FileConfig <batconf.sources.file.FileConfig>`
* Add .ini config source :py:class:`IniConfig <batconf.sources.ini.IniConfig>`
* Add .toml config source :py:class:`TomlConfig <batconf.sources.toml.TomlConfig>`
* Make the pyyaml dependency optional
* Make [toml] an optional extra for Python version < 3.11
* Docs: added a migration guide for v0.1 -> v0.2
* Added Example Jupyter Notebook to `notebooks <https://github.com/lundybernard/batconf/tree/main/notebooks/>`_
* Modify :`Example Project <https://github.com/lundybernard/batconf/tree/main/tests/example>`_
  to use .ini instead of .yaml
* Update `Example Project <https://github.com/lundybernard/batconf/tree/main/tests/example>`_
  to use freeform Schemas, instead of schemas bound to module namespaces.
* Add default parameters to Configuration class:

  * The Configuration class now handles default values set in Config
    dataclasses.  As a result, we no longer need the DataclassConfig source
    to lookup default values.
  * Improve Configuration repr for paths and child-configs
  * Remove DataclassConfig from example code and docs
* Add _path attribute to :py:class:`Configuration <batconf.manager.Configuration>`
* Lint with Ruff


.. _v0.1.8:

--------------------
0.1.8 - 2024-08-09
--------------------

Observability improvements

* Add expressive repr to Configuration class

Project maintenance

* Improve documentation
* Add security policy
* Add project logo
* Add optional extras for dev and docs

.. _v0.1.7:

--------------------
0.1.7 - 2024-06-13
--------------------

* Add support for python3.12
* Various improvements to type hints
* Add design principles section to :gh-file:`README <README.md>`

.. _v0.1.6:

--------------------
0.1.6 - 2023-07-19
--------------------

* Unpin pyyaml dependency
