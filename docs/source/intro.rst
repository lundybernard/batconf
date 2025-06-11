.. currentmodule:: batconf

.. toctree::
   :hidden:
   :maxdepth: 2


Introduction
============

Designed to provide 12-factor compliant configuration management
for python microservices, applications, and automation tools.

Provides builtin support for hierarchical configuration via:

* CLI args
* Environment Variables
* Config Files (ini, toml, yaml)
* Config classes with default values
* Fully customizeable configuration Schemas

Users can create their own config sources
by creating classes that satisfy
:py:class:`SourceInterfaceProto <batconf.source.SourceInterfaceProto>`
(or subclass :py:class:`SourceInterface <batconf.source.SourceInterface>`)

The config lookup order is determined by the
:py:class:`SourceList <batconf.source.SourceList>` instance,
which can be adjusted to suit your needs.


Motivation
----------
This module was created to serve the configuration needs of python projects,
especially microservices, command line applications, and service clients.

I encountered many cases where we wanted to define reasonable default configs,
we wanted to use a config file for values which changed infrequently,
we wanted to override those values with Environment variables when running
services, and we wanted commandline arguments to take priority over any other
configuration setting.

BatConf provides a way to define arbitrary configuration sources
(cli args, ENV variables, config files, web-services, etc.) and access them in
a user-defined priority order.


Composable Configuration Sources
--------------------------------
This diagram illustrates how sources with higher priority override values
from lower priority sources to compose the runtime configuration.

.. image:: _static/config_composition.png
   :alt: Configuration Sources Diagram


Limitations
-----------
- All config values should™ return strings.
  This is a best practice, as some sources (like ENV) cannot store/return
  non-string values.
  This can be abused as desired if you are very careful.

- Falsey values cannot be returned.
  This is not a problem if all values are strings ("False" or "None" are valid
  config values), but if a config source returns ``False`` or ``None``
  they are treated as missing values.
