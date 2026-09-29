.. currentmodule:: batconf

Stability and Scope
===================

From v1.0.0 the BatConf API is frozen. This page states what that
covers, how changes reach you, and what BatConf will not grow into.


Versioning
----------
BatConf follows `Semantic Versioning <https://semver.org/>`_.

* **Major** (``2.0.0``) — a documented behaviour changes, or a public
  name is removed. Only a major release may break working code.
* **Minor** (``1.1.0``) — new capability, and the release that carries
  out removals announced in an earlier patch release.
* **Patch** (``1.0.1``) — fixes, documentation, and new deprecation
  warnings. No removals.


What the freeze covers
----------------------
The public API is everything reachable without a leading underscore
from:

* the ``batconf`` root namespace — :class:`~batconf.manager.Configuration`,
  :class:`~batconf.lib.ConfigSingleton`, :class:`~batconf.source.SourceList`,
  :func:`~batconf.lib.insert_source`, the source classes, and the error
  classes;
* :mod:`batconf.types` and :mod:`batconf.sources.types` — the Protocol
  types, including
  :py:class:`SourceInterfaceP <batconf.sources.types.SourceInterfaceP>`,
  which third-party sources are written against;
* the constructor arguments of the built-in sources, and the
  ``get(key, path)`` signature every source implements;
* the config file layouts described in :doc:`guide`.

A name with a leading underscore is internal. It can change in any
release, including a patch.


Deprecation policy
------------------
Nothing is removed without warning first, and the warning ships in a
release you can run:

1. **Announce in a patch release** (``n.n.x``). The name still works
   and emits a ``DeprecationWarning`` that names both its replacement
   and the version that will remove it. The :doc:`migration` guide
   gains an entry the same release.
2. **Remove in the next minor** (``n.x``).

So a name deprecated in ``1.2.3`` still works in every later ``1.2.x``
and is removed in ``1.3.0``.

To find deprecated names before they go, run your test suite with
deprecation warnings promoted to errors:

.. code-block:: ini
    :caption: pyproject.toml

    [tool.pytest.ini_options]
    filterwarnings = ["error::DeprecationWarning"]

Each failure points at one line to change.


Non-goals
---------
Some things BatConf deliberately leaves to you. They are not gaps
waiting to be filled, and a 1.0 promise is as much about what will not
appear as about what stays:

* **Validation.** BatConf composes sources and returns their values.
  Checking those values belongs in your application, scoped to what it
  actually needs, and BatConf will not tie you to a validation library.
* **Configuration is not data.** BatConf handles the human interface of
  application configuration. It is not a data-ingestion tool.
* **Your entry point stays yours.** BatConf never parses ``argv``,
  never installs a CLI, and its imports can be confined to one module.

BatConf is aimed at small applications, developer and automation
tooling, and scientific-Python projects that want layered
configuration without a framework taking over. See :doc:`comparison`
for how that compares with other tools, and for the cases where
another tool is the better fit.
