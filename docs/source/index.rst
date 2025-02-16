=======================
Welcome to BatConf
=======================

Configuration Management for Python projects, modules, applications,
and microservices.

Compose structured hierarchical configurations from multiple sources.
Enable your code to adapt seamlessly to the current context.
Allow users in different contexts to use the config source
that works best for them.

* Hierarchical priority: CLI > Environment > config file > module defaults
* Provides builtin support for common config sources:

  * CLI args
  * Environment Variables
  * Config File (yaml)
  * Config classes with default values
* Easily extendable, add new sources to serve your needs.
* Set reasonable defaults, and override them as needed.
* Designed for 12-factor applications (config via Environment Variables)


.. image:: https://img.shields.io/pypi/v/batconf?color=blue
   :target: https://pypi.org/project/batconf/
.. image:: https://github.com/lundybernard/batconf/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/lundybernard/batconf/actions
.. image:: https://img.shields.io/pypi/pyversions/batconf
.. image:: https://img.shields.io/pypi/dm/batconf
   :target: https://pypistats.org/packages/batconf


New Dev Blog!
-------------

Check out the :ref:`upcoming_changes_in_02x`

- Optional pyyaml dependency
- More flexible config structures
- New config file sources (.ini, .toml)


Professional Support
---------------------

.. image:: _static/Tidelift_Logos_RGB_Tidelift_Mark_On-White.png

Professionally supported BatConf is now available.

Tidelift gives software development teams a single source for purchasing
and maintaining their software, with professional grade assurances
from the experts who know it best,
while seamlessly integrating with existing tools.

`Get supported BatConf with the Tidelift subscription
<https://tidelift.com/subscription/pkg/pypi-batconf?utm_source=pypi-batconf&utm_medium=readme>`__


Contributing
-------------

All contributions, bug reports, bug fixes, documentation improvements,
enhancements, and ideas are welcome.

Check out one of these good first issues to help with:

* `Cleanup Sphinx documentation <https://github.com/lundybernard/batconf/issues/32>`__
* `Add support for Python 3.13 <https://github.com/lundybernard/batconf/issues/53>`__

Issues
------

Submit issues, feature requests or bugfixes
on `GitHub <https://github.com/lundybernard/batconf>`__


License and Credits
-------------------

``batconf`` is licensed under the
`MIT license <https://github.com/lundybernard/batconf/blob/main/LICENSE.txt>`__.
and is written and maintained by Lundy Bernard (lundy.bernard@gmail.com)
and Lauren Moore


Indices and tables
==================

* :ref:`genindex`

.. currentmodule:: batconf

.. toctree::
   :hidden:
   :caption: Introduction
   :maxdepth: 2

   intro
   quickstart
   devguide

.. toctree::
   :hidden:
   :caption: Reference
   :maxdepth: 2

   changelog
   reference/modules
