=========
Changelog
=========

This is a record of BatConf releases and what went into them,
in reverse chronological order.
All previous releases should still be available
:pypi:`on PyPI <batconf>`.


BatConf 0.x
==============

.. _v0.4.1:

------------------
0.4.1 - TBD
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
