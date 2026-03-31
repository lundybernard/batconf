.. currentmodule:: batconf

.. toctree::
   :hidden:
   :maxdepth: 2


User Guide
==========


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


Custom Configuration Sources
-----------------------------

Any object with a ``get(key, path)`` method satisfies
:py:class:`SourceInterfaceProto <batconf.source.SourceInterfaceProto>`,
so you can pull config values from any backend — a secrets manager,
a database, a remote API — without changing the rest of your config setup.

Using the Protocol (structural subtyping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The simplest approach: implement ``get`` on any class, no base class required.

.. code-block:: python

    class VaultSource:
        def __init__(self, client):
            self._client = client

        def get(self, key: str, path: str | None = None) -> str | None:
            full_key = f'{path}.{key}' if path else key
            return self._client.read(full_key)

Subclassing ``SourceInterface``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Subclassing :py:class:`SourceInterface <batconf.source.SourceInterface>`
gives you the ABC enforcement and is useful if you want type checkers to
flag incomplete implementations.

.. code-block:: python

    from batconf.source import SourceInterface

    class VaultSource(SourceInterface):
        def __init__(self, client):
            self._client = client

        def get(self, key: str, path: str | None = None) -> str | None:
            full_key = f'{path}.{key}' if path else key
            return self._client.read(full_key)

Registering a custom source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pass your custom source to :class:`~batconf.source.SourceList` like any
built-in source, or add it at runtime with :func:`~batconf.lib.insert_source`:

.. code-block:: python

    from batconf import insert_source
    from yourmodule.conf import CFG

    insert_source(cfg=CFG, source=VaultSource(vault_client))

The source is inserted at index 0 by default, giving it the highest
priority. Pass ``index=`` to place it elsewhere in the lookup order.

Important constraints
~~~~~~~~~~~~~~~~~~~~~
* ``get`` must return a ``str`` or ``None`` — never a non-string value.
  Some sources (e.g. environment variables) can only store strings, and
  BatConf treats any falsey return value (``False``, ``None``, ``""``)
  as "not found".
* Keep ``get`` fast and side-effect-free — it is called on every config
  lookup, not cached by BatConf itself.
