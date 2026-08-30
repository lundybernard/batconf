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
same pair: it joins the path and the key, replaces each ``.`` with
``_``, and upper-cases the result.

* path ``project.database``, key ``host`` → ``PROJECT_DATABASE_HOST``
* path ``project``, key ``timeout`` → ``PROJECT_TIMEOUT``
* no path, key ``host`` → ``BAT_HOST``

The ``BAT`` prefix stands in for a missing path.
:class:`~batconf.manager.Configuration` always supplies one, so the
prefix appears only when the source is queried directly.


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

Handle a missing ``path``. A :class:`~batconf.manager.Configuration`
always passes one, but application code and tests may call ``get`` with
a key alone.


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
