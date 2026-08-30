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
  * Config File (ini, toml, yaml)
  * Config classes with default values
  * Fully customizeable configuration Schemas

* Customizable priority: the ``SourceList`` sets the lookup order,
  and you can change it
* Easily extendable, add new sources to serve your needs.
* Set reasonable defaults, and override them as needed.
* Designed for 12-factor applications (config via Environment Variables)
* :class:`~batconf.lib.ConfigSingleton`: share one configuration across
  your application, and :func:`~batconf.lib.insert_source` to add a
  source at runtime
* Subscript access: ``cfg['key']`` alongside ``cfg.key``, for dynamic
  lookups like ``cfg.clients[client_id]``
* One error base: catch every configuration failure with
  :class:`~batconf.errors.BatconfError`


.. image:: https://img.shields.io/pypi/v/batconf?color=blue
   :target: https://pypi.org/project/batconf/
.. image:: https://github.com/lundybernard/batconf/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/lundybernard/batconf/actions
.. image:: https://img.shields.io/pypi/pyversions/batconf
.. image:: https://img.shields.io/pypi/dm/batconf
   :target: https://pypistats.org/packages/batconf


| Source code: https://github.com/lundybernard/batconf
| PyPi: https://pypi.org/project/batconf/


Free-Threading support!
-----------------------

Read about how BatConf supports free-threading/nogil in python 3.14+

:ref:`freethreading_blog`


Security
--------

Read about how BatConf helps to protect you against supply chain attacks
on our Developer's Blog.

:ref:`supplychain_security_blog`


What's new in v1.0.0
--------------------

- The API is frozen. See :doc:`stability` for what that covers and how
  deprecations are handled from here.
- :class:`~batconf.errors.BatconfError` — every failure batconf raises
  carries a batconf type, while keeping its standard exception base
- A missing config file is reported when the source is built, not at
  the first lookup
- A walk-through for :doc:`writing a custom source <guide>`, and the
  config file contract stated in full

See the :doc:`migration` guide for upgrade instructions.


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
------------------

* :ref:`genindex`

.. currentmodule:: batconf

.. toctree::
   :hidden:
   :caption: Introduction
   :maxdepth: 2

   intro
   quickstart
   guide
   comparison

.. toctree::
   :hidden:
   :caption: Developer's Guide
   :maxdepth: 2

   devguide

.. toctree::
   :hidden:
   :caption: News and Announcements
   :maxdepth: 2

   devblog

.. toctree::
   :hidden:
   :caption: Reference
   :maxdepth: 2

   stability
   changelog
   migration
   reference/modules
