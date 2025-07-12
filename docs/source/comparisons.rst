
BatConf Implicit Opinions:
==========================

Configuration values should be Strings
______________________________________

* Environment Variables are strings
  * Supporting types with environment variables requires interpolation

* Commandline arguments are strings, until they are interpolated.

* Interpolation of input strings is not a direct concern of config management
  * It is extremely difficult, or impossible, to provide interpolation which
    will satisfy all users.
  * Different parts of an application (logging vs computation)
    may require different types, and setting types on load can lead to conflicts.

* It is better to load config values as strings, and allow users to interpolate
  those strings in a separate layer, to meet the needs of thier application.

Configuration schemas should be reusable
----------------------------------------
If we have an Client from a package, which is configurable using BatConf.
An application which utilizes the Client, should be able to utilize its schema.

.. code-block:: Python
    from clientlib.conf import ClientSchema

    @dataclass
    class ApplicationSchema:
        client1: ClientSchema
        client2: ClientSchema


betterconf:
===========

Both:
-----
* require no additional 3rd party dependencies, only Python's stdlib
* Support user-provided arbitrary configuration sources

Pro betterconf:
---------------
* betterconf allows type-casting config values
* Less boilerplate, betterconf's Config class creation is a bit more terse
  than BatConf's

Pro BatConf:
------------
* Hierarchical configuration sources.
  It looks like this is *possible* with betterconf, but not simple.
* Distributed config definitions: BatConf config schemas can be built from
  python dataclasses, allowing modules to define their own configuration schemas
  without the need to import anything from BatConf.
* Composability: BatConf's Schemas are designed to be composable from 
  sub-modules and 3rd party packages.


ConfZ:
======

Both:
_____
* Hierarchical configuration sources
* User-defined config sources
* Nested / Namespaced configurations

Pro ConfZ:
----------
* Casting values using Pydantic.
* Advanced value validation options.

Pro BatConf:
------------
* Zero required dependencies for supplychain safety.
* Favors composition over inheritance, and avoids tight-coupling
  with your code-base.


OmegaConf:
==========

Both:
-----
* Hierarchical configuration sources (with very different approaches)
* Multiple configuration files for separation of concerns
* Structured configurations using dataclasses
* Dot-notation access for config values

Pro OmegaConf:
--------------
* Serialization: save and load configurations to file (planned future feature of BatConf)
* Typed values and type-checking
* Supports more dynamic creation of Configuration objects, such as configs from lists and dicts.
* Variable Interpolation

Pro BatConf:
------------
* Zero required dependencies for supplychain safety (PyYaml is an optional extra)
* Simplicity:
  * Preffers static schemas
  * values as strings (parsing to types is a separate concern)
  * focus on settings which humans interact with, not meta-programming.
* Streamlined Hierarchy of config sources (SourceList, instead of Merging and resolvers)
* Multiple environments (dev, staging, production, etc.) in config files
