```{currentmodule} batconf
```

```{toctree}
:hidden: true
:maxdepth: 2
```

# Introduction

Designed to provide 12-factor compliant configuration management
for python microservices, applications, and automation tools.

Provides builtin support for hierarchical configuration via:

* CLI args
* Environment Variables
* Config File (yaml)
* Config classes with default values

Users can create their own config sources
by creating classes that satisfy `batconf.source.SourceInterfaceProto`
(or subclass `batconf.source.SourceInterface`)

The config lookup order is determined by the `SourceList` instance,
which can be adjusted to suit your needs.

## Motivation

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

## Composable Configuration Sources

![Configuration Sources Diagram](/_static/configuration_sources.png)

## Limitations

- Some features (ENV variable names, and sub-module config lookups) are
  `__module__` dependent.  
  The configuration tree structure is also linked to
  the python module namespace.  
  We now consider this a defect, and have plans to decouple
  the config-tree-paths from the module namespace in v0.2

- All config values should™ return strings.  
  This is a best practice, as some sources (like ENV) cannot store/return
  non-string values.  
  This can be abused as desired if you are very careful.

- Falsey values cannot be returned.
  This is not a problem if all values are strings ("False" or "None" are valid
  config values), but if a config source returns `False` or `None`
  they are treated as missing values.
