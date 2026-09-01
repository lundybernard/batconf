.. currentmodule:: batconf

.. toctree::
   :hidden:
   :maxdepth: 2


User Guide
==========


Source lookup rules
-------------------

:class:`~batconf.manager.Configuration` asks every source for a ``key``
and the dotted ``path`` of the config node holding it. Each source turns
that pair into a lookup its own way, and the rule decides how you name
things outside BatConf.


NamespaceSource
~~~~~~~~~~~~~~~
:class:`~batconf.sources.argparse.NamespaceSource` joins the path and the
key with a ``.``, then reads that one attribute off the
:class:`argparse.Namespace`:

.. code-block:: python

    getattr(namespace, 'yourproject.server.host', None)

Three consequences follow:

* Every argument needs a ``dest`` holding its full dotted config path::

    parser.add_argument('--host', dest='yourproject.server.host')

* There is no bare-key fallback. An argument stored as ``host`` is never
  found by a lookup for ``yourproject.server.host``.
* Nested namespaces never resolve. A ``Namespace`` holding another
  ``Namespace`` is not walked — only the flat attribute name is read.


EnvSource
~~~~~~~~~
:class:`~batconf.sources.env.EnvSource` builds a variable name from the
same pair, led by the ``prefix`` you declare: it joins the prefix, the
path and the key, replaces each ``.`` with ``_``, and upper-cases the
result. With ``EnvSource(prefix='yourproject')``:

* path ``database``, key ``host`` → ``YOURPROJECT_DATABASE_HOST``
* path ``server``, key ``timeout`` → ``YOURPROJECT_SERVER_TIMEOUT``
* no path, key ``host`` → ``YOURPROJECT_HOST``

Declare a prefix. The process environment is shared by every program the
shell starts, and the prefix is the one namespace in it that your
project owns.

.. warning::

   ``BATCONF_`` is reserved for BatConf's own variables. Do not choose
   it as your prefix.

Without a prefix, a key at the root would resolve to a bare uppercase
name — ``PATH``, ``HOME``, ``USER``. Those are ambient process
variables: the value comes from the shell that started the program, it
outranks your config file, and nothing in the result tells it apart from
a value you set. ``EnvSource`` refuses that lookup and returns ``None``,
so the schema default applies instead:

.. code-block:: python

    >>> import os
    >>> os.environ['SERVER_HOST'] = 'localhost'
    >>> EnvSource().get('path')  # returns None: a bare name is refused
    >>> EnvSource().get('host', path='server')
    'localhost'

``EnvSource(raw=True)`` lifts the guard. It is raw environment access:
schema-declared fields resolve against ambient variables, ``cfg.path``
reads ``$PATH``, and the collision risk is yours to accept.


The path is the mount point
~~~~~~~~~~~~~~~~~~~~~~~~~~~
``path`` names where a schema hangs in every source at once. An absent
or empty path mounts the schema at the root, and each
sub-configuration mounts under its field name:

.. code-block:: python

    Configuration(source_list, YourSchema)                 # at the root
    Configuration(source_list, YourSchema, path='yourproject')

A schema resolves the same names either way: it mounts at the root when
it stands alone, and under a field name when a larger schema holds it.
Several top-level schemas therefore hang under one configuration — the
parent is a :class:`~batconf.manager.Configuration` with no path.

The root belongs to no project. In a file or a process environment that
two projects share, each one declares its own name; see
:ref:`sharing-a-file`.


Configuration file contract
---------------------------

:class:`~batconf.sources.ini.IniSource`,
:class:`~batconf.sources.toml.TomlSource` and
:class:`~batconf.sources.yaml.YamlSource` read the same three layouts,
selected with the ``file_format`` argument. The rules below hold for
all three sources. :doc:`quickstart` shows a file in each format.


Values are strings
~~~~~~~~~~~~~~~~~~
Write every config value as a string. Config files, environment
variables and CLI arguments all deliver text, and the schema keeps only
``str`` defaults, so a string is the one type every layer of the lookup
agrees on.

A key that resolves to a section, table or mapping is not a value. The
source returns ``None`` for it and the lookup moves on to the next
source.

.. warning::

   ``TomlSource`` is the one source that can hand back another type.
   TOML parses ``retries = 5`` as an integer and the value reaches your
   code as an ``int``. Quote TOML values — ``retries = '5'`` — to stay
   inside the string contract. ``IniSource`` and ``YamlSource`` return
   strings whatever the file says.


``environments`` — the default layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The top level of the file is a set of named environments. One reserved
top-level key, ``batconf``, is not an environment: it holds
``default_env``, whose value must name one of the others.

.. code-block:: ini
    :caption: config.ini

    [batconf]
    default_env = dev

    [dev]
    [dev.yourproject.server]
    host = localhost

    [prod]
    [prod.yourproject.server]
    host = 10.0.0.1

* A source reads inside one environment only. Everything outside the
  selected environment is invisible to it, including the other
  environments.
* ``config_env='prod'`` on the source overrides ``default_env``.
* Naming an environment the file does not define raises
  :class:`~batconf.errors.ConfigEnvironmentNotFound` on the first read.
* In an INI file the environment section itself must exist — ``[dev]``,
  even when empty. Deeper sections are literal dotted names, so
  ``[dev.yourproject.server]`` needs no ``[dev.yourproject]`` above it.


``sections``
~~~~~~~~~~~~
The environment layer is dropped and the top level is the config tree
itself. Use it when one file serves one environment.

.. code-block:: ini
    :caption: config.ini (file_format='sections')

    [yourproject.server]
    host = localhost

There is no ``batconf`` key in this layout, and ``config_env`` is
ignored. One ``sections`` file holds several projects, each under its
own top-level name, for one environment.

An INI file needs the whole dotted path as a literal section name, and
``configparser`` has no unnamed section. A key at the root of a schema
therefore lives in the reserved ``[/ROOT/]`` section:

.. code-block:: ini
    :caption: config.ini (file_format='sections')

    [/ROOT/]
    name = demo

    [server]
    host = localhost

``[/ROOT/]`` is not recommended; it exists so that no schema becomes
unreadable purely because the file is INI. A project with its own INI
file mounts under its own name instead. The name is case-sensitive, so
``[/root/]`` does not resolve. TOML and YAML hold root keys natively and
have no reserved section.


``flat``
~~~~~~~~
No sections at all: every key lives at the root of the file.

.. code-block:: ini
    :caption: config.ini (file_format='flat')

    host = localhost
    port = 5000

INI keys are taken literally, dots included, so ``not.really.nested``
is one key rather than a path.

A flat file is a root-level file: every key sits at the root, so mount
the schema at the root and all three sources agree.

.. warning::

   Give a flat file a ``path`` and the three sources disagree.
   ``IniSource`` ignores the path and still reads from the root.
   ``TomlSource`` and ``YamlSource`` prepend the path before walking,
   find nothing, and return ``None``. Read a flat file through a
   :class:`~batconf.manager.Configuration` with no path.


Selecting an environment
------------------------

``BATCONF_ENVIRONMENT`` is the canonical shell-level environment
selector: one variable that names the environment for every tool started
in that shell. It is canonical, not enforced — a project may select its
environment another way.

No source reads it. A source reads one medium and answers for one key;
which environment the program runs in is not a fact about a medium. The
caller decides once, at construction, and passes ``config_env=``.

Precedence is fixed:

1. an explicit ``config_env=``,
2. a command-line argument, read by a bootstrap configuration,
3. ``BATCONF_ENVIRONMENT``, read by the same bootstrap,
4. the file's ``default_env``.


The two-stage bootstrap
~~~~~~~~~~~~~~~~~~~~~~~
Which environment to select, and which config file to read, must be
known before the configuration that would describe them can be built.
Build a small one first. A bootstrap
:class:`~batconf.manager.Configuration` mounts at the root over the
command-line arguments and an ``EnvSource`` in the reserved namespace,
and carries the environment name, the config file, and any other
pre-configuration value:

.. code-block:: python

    from argparse import Namespace
    from dataclasses import dataclass

    from batconf import (
        Configuration,
        EnvSource,
        IniSource,
        NamespaceSource,
        SourceList,
    )


    @dataclass
    class BootSchema:
        environment: str
        config_file: str = 'config.ini'


    def get_config(
        cli_args: Namespace | None = None,
        config_env: str | None = None,
    ) -> Configuration:
        # stage 1: what must be known before the real configuration
        boot = Configuration(
            source_list=SourceList([
                NamespaceSource(cli_args) if cli_args else None,
                EnvSource(prefix='batconf'),
            ]),
            config_class=BootSchema,
        )

        # stage 2: the real configuration, from the bootstrap values
        config_file = IniSource(
            file_path=boot.config_file,
            # None falls through to the file's default_env
            config_env=config_env or getattr(boot, 'environment', None),
        )
        return Configuration(
            source_list=SourceList([
                NamespaceSource(cli_args) if cli_args else None,
                EnvSource(prefix='yourproject'),
                config_file,
            ]),
            config_class=YourSchema,
            path='yourproject',
        )

:class:`~batconf.source.SourceList` drops ``None`` entries, so a run
with no command line reads the environment alone.

Combining the two sources is what earns the bootstrap its schema. One
source reads one variable and needs no schema; two need an order and a
name for each value, which is what ``BootSchema`` declares.

``config_file`` belongs there because the file itself is worth changing
at runtime. ``--config-file config-failsafe.ini``, or
``BATCONF_CONFIG_FILE``, swaps the whole file for one run — the answer
when a different environment is not the one you want.

The bootstrap is an ordinary configuration, so the pattern needs no new
machinery. It mounts at the root, so it needs no namespace of its own,
and each argument takes a bare field name as its ``dest``:
``--config-env`` stores ``environment``, ``--config-file`` stores
``config_file``. Reading the reserved ``BATCONF_`` namespace here is
its one sanctioned use.

``getattr`` supplies the fallthrough: a value the bootstrap cannot
resolve raises
:class:`~batconf.errors.ConfigValueNotFound`, which is an
``AttributeError``, so ``None`` reaches the source and the file's
``default_env`` decides.


.. _sharing-a-file:

Sharing a file or a process environment
---------------------------------------

The environment dimension exists only where the medium expresses it.
BatConf documents the contract and adds no layer of its own.

* Only ``environments`` holds several environments in one file.
  ``flat`` and ``sections`` carry no environment and ignore
  ``config_env``, silently.
* ``sections`` holds several projects in one file, for one environment.
* ``flat`` is single-tenant: one key space, so two projects cannot both
  declare ``host``.
* Environment variables carry no environment. The process environment
  *is* the environment.

In a shared file or a shared process environment, every project declares
its own name — its ``path``, and its ``EnvSource`` prefix — on every
source it builds. The file root and the process-environment root belong
to no one, so a project that leaves its name unset claims the shared
root, and so does every other project that does the same. BatConf cannot
detect this: it cannot know that a file is shared.

Two further consequences of a shared file:

* Every project reading it must agree on one ``file_format``. An
  ``environments`` file read as ``sections`` returns nothing.
* One file holds one ``default_env``, and the file owns it. A project
  that wants a different environment passes ``config_env=``.

.. warning::

   An exported variable outlives every edit to the file. It keeps
   overriding the file in every environment until it is unset. This is
   the sharpest hazard in the shared case.

.. warning::

   In INI, ``[DEFAULT]`` keys inherit into every declared section, so
   one project can leak a key into every other project's sections.


Testing
-------

Testing with a ``ConfigSingleton``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Because a :class:`~batconf.lib.ConfigSingleton` is shared across your
application, tests that modify it can affect each other. Use
:meth:`~batconf.lib.ConfigSingleton._reset` in ``tearDown`` to restore
the singleton to a clean state after each test.

.. code-block:: python

    from unittest import TestCase
    from yourmodule.conf import CFG

    class MyTests(TestCase):
        def tearDown(t):
            CFG._reset()

        def test_with_override(t):
            from batconf import insert_source, NamespaceSource
            from argparse import Namespace
            args = Namespace()
            setattr(args, 'yourmodule.server.host', 'testhost')
            insert_source(cfg=CFG, source=NamespaceSource(args))
            t.assertEqual(CFG.server.host, 'testhost')

        def test_reads_default(t):
            # CFG was reset by tearDown — reads from the real sources again
            t.assertEqual(CFG.server.host, 'localhost')


Testing without a singleton
~~~~~~~~~~~~~~~~~~~~~~~~~~~
If test isolation is a concern, call ``get_config()`` directly in each
test instead of using the shared ``CFG``. This creates a fresh
:class:`~batconf.manager.Configuration` per test with no shared state.

.. code-block:: python

    from yourmodule.conf import get_config

    class MyTests(TestCase):
        def test_something(t):
            cfg = get_config()
            t.assertEqual(cfg.server.host, 'localhost')


Writing a custom configuration source
-------------------------------------

A configuration source is any object with a ``get`` method. Nothing
else is required — no base class, no registration, no metadata — so a
source can read from a secrets manager, a database, a remote API, or a
file format BatConf does not ship.


The contract
~~~~~~~~~~~~
:class:`~batconf.source.SourceList` calls every source the same way:

.. code-block:: python

    def get(self, key: str, path: str | None = None) -> str | None: ...

* ``key`` is the option name.
* ``path`` is the dotted path of the config node holding it, for example
  ``yourproject.server``. It is passed **positionally**, so name your
  second parameter freely but keep it second.
* Return the value as a ``str``, or ``None`` when the source has no
  value. :class:`~batconf.source.SourceList` walks its sources in order
  and stops at the first truthy return, so ``None`` means "ask the next
  source".

That is the whole interface, and it is what
:py:class:`SourceInterfaceP <batconf.sources.types.SourceInterfaceP>`
declares.


Step 1: the smallest source
~~~~~~~~~~~~~~~~~~~~~~~~~~~
A source backed by a flat dict of fully-qualified keys is enough to
start. Joining ``path`` and ``key`` gives the lookup key:

.. code-block:: python

    class DictSource:
        """Read config values from a flat dict of dotted keys."""

        def __init__(self, values: dict[str, str]) -> None:
            self._values = values

        def get(self, key: str, path: str | None = None) -> str | None:
            return self._values.get(f'{path}.{key}' if path else key)

Use it like any built-in source:

.. code-block:: python

    >>> src = DictSource({'yourproject.server.host': 'localhost'})
    >>> src.get('host', path='yourproject.server')
    'localhost'
    >>> src.get('port', path='yourproject.server')  # returns None

Handle an absent ``path``. A schema mounted at the root passes the empty
string, and application code and tests may call ``get`` with a key
alone. Both mean the root of your medium.


Step 2: a file-backed source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Most real sources hold nested data and need to load it. This JSON
source walks the dotted path through the parsed document:

.. code-block:: python

    from functools import cached_property
    from json import loads
    from pathlib import Path
    from typing import Any

    from batconf.errors import ConfigFileNotFound


    class JsonSource:
        """Read config values from a nested JSON file."""

        def __init__(self, file_path: str) -> None:
            self._file_path = Path(file_path)
            if not self._file_path.exists():
                raise ConfigFileNotFound(
                    f'Config file not found: {self._file_path}'
                )

        @cached_property
        def _data(self) -> dict:
            return loads(self._file_path.read_text())

        def get(self, key: str, path: str | None = None) -> str | None:
            parts = f'{path}.{key}'.split('.') if path else key.split('.')
            node: Any = self._data
            for part in parts:
                if not isinstance(node, dict):
                    return None
                node = node.get(part)
            return node if isinstance(node, str) else None

Three habits worth copying from the built-in sources:

* **Validate the path in the constructor.** Reporting a bad path while
  the caller still holds it beats failing at the first read, from
  somewhere else entirely.
* **Load lazily, once.** ``_data`` is a
  :class:`~functools.cached_property`, so the file is read on the first
  lookup and never again. A source that is never queried never touches
  the disk.
* **Return only strings.** The final ``isinstance`` check turns a
  number, a boolean or a nested object into ``None``, so a key that
  resolves to a branch rather than a leaf falls through to the next
  source instead of returning a ``dict``.

Given ``conf.json``:

.. code-block:: json

    {"yourproject": {"server": {"host": "json-host"}}}

.. code-block:: python

    >>> src = JsonSource('conf.json')
    >>> src.get('host', path='yourproject.server')
    'json-host'


Step 3: register the source
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pass it to :class:`~batconf.source.SourceList` alongside the built-in
sources. Position decides priority — earlier wins:

.. code-block:: python
    :caption: yourmodule/conf.py

    source_list = SourceList([
        NamespaceSource(cli_args) if cli_args else None,
        EnvSource(),
        JsonSource('conf.json'),
        IniSource(CONFIG_FILE_NAME),
    ])

``None`` entries are dropped, so a source can be included conditionally
on one line.

To add one after the fact — for example once CLI arguments are parsed —
use :func:`~batconf.lib.insert_source`:

.. code-block:: python

    from batconf import insert_source
    from yourmodule.conf import CFG

    insert_source(cfg=CFG, source=JsonSource('conf.json'))

The source lands at index 0, the highest priority. Pass ``index=`` to
place it elsewhere in the lookup order.


Declaring the Protocol
~~~~~~~~~~~~~~~~~~~~~~
Subclass
:py:class:`SourceInterfaceP <batconf.sources.types.SourceInterfaceP>`
to have a type checker flag an incomplete implementation. The built-in
sources are written this way. Runtime behaviour is identical — the
Protocol is satisfied structurally either way:

.. code-block:: python

    from batconf.sources.types import SourceInterfaceP

    class JsonSource(SourceInterfaceP):
        ...

:py:class:`SourceInterfaceP <batconf.sources.types.SourceInterfaceP>` is
runtime-checkable, so ``isinstance(src, SourceInterfaceP)`` also works.


Reporting failures
~~~~~~~~~~~~~~~~~~
Raise a subclass of :class:`~batconf.errors.BatconfError` when the
source cannot do its job, so a caller can catch every configuration
failure with one clause. Reuse an existing error where it fits — the
JSON source above raises
:class:`~batconf.errors.ConfigFileNotFound` — or derive your own:

.. code-block:: python

    from batconf.errors import BatconfError

    class VaultUnreachable(BatconfError, ConnectionError):
        """The secrets backend did not answer."""

Keeping the standard exception as a second base is what the built-in
errors do, and it lets callers who catch ``ConnectionError`` keep
working.

A key that is simply absent is not a failure. Return ``None`` and let
the next source answer.


Testing a custom source
~~~~~~~~~~~~~~~~~~~~~~~
Test ``get`` directly — it takes two strings and returns one:

.. code-block:: python

    class JsonSourceTests(TestCase):
        def test_get(t):
            src = JsonSource('tests/data/conf.json')

            with t.subTest('resolves a path and key'):
                t.assertEqual(src.get('host', path='app.server'), 'localhost')

            with t.subTest('a missing key returns None'):
                t.assertIsNone(src.get('nope', path='app.server'))

            with t.subTest('a branch is not a value'):
                t.assertIsNone(src.get('server', path='app'))

Then check it composes, by putting it in a
:class:`~batconf.source.SourceList` behind a source that has no value
for the key and confirming yours answers.


Rules to follow
~~~~~~~~~~~~~~~
* ``get`` returns a ``str`` or ``None``, never another type. BatConf
  treats any falsey return (``None``, ``''``, ``False``, ``0``) as
  "not found" and moves to the next source.
* ``get`` runs on every lookup. BatConf caches nothing, so cache inside
  the source if the backend is slow.
* Keep ``get`` free of side effects. It is called during attribute
  access, including while rendering a configuration for display.
