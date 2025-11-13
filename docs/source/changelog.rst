=========
Changelog
=========

This is a record of BatConf releases and what went into them,
in reverse chronological order.
All previous releases should still be available
:pypi:`on PyPI <batconf>`.


BatConf 0.x
==============

.. only:: has_release_file

    --------------------
    Current pull request
    --------------------

    .. include:: ../RELEASE.rst

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
