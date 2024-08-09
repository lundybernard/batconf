---
file_format: mystnb
---

% batconf documentation entrypoint

```{currentmodule} batconf
```

```{toctree}
:caption: Introduction
:hidden: true
:maxdepth: 2

Welcome to BatConf <self>
Intro <intro>
Quick Start Guide <quickstart>
Dev Guide <devguide>
```

```{toctree}
:caption: Reference
:hidden: true
:maxdepth: 6

Changelog <changelog>
API <reference/modules>
```

# Welcome to BatConf

Configuration Management for Python projects, modules, applications, 
and microservices.

Compose structured hierarchical configurations from multiple sources.
Enable your code to adapt seemlessly to the current context.
Allow users in different contexts to use the config source that works best for
them.

* Hierarchical priority: CLI > Environment > config file > module defaults
* Provides builtin support for common config sources:
  * CLI args
  * Environment Variables
  * Config File (yaml)
  * Config classes with default values
* Easily extendable, add new sources to serve your needs.
* Set reasonable defaults, and override them as needed.
* Designed for 12-factor applications (config via Environment Variables)


[![Stable Version](https://img.shields.io/pypi/v/batconf?color=blue)](https://pypi.org/project/batconf/)
[![Build Status](https://github.com/lundybernard/batconf/actions/workflows/tests.yml/badge.svg)](https://github.com/lundybernard/batconf/actions)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/batconf)
[![Downloads](https://img.shields.io/pypi/dm/batconf)](https://pypistats.org/packages/batconf)


## Contributing

All contributions, bug reports, bug fixes, documentation improvements,
enhancements and ideas are welcome.

Check out one of these good first issues to help with:
* [Cleanup Sphinx documentation](https://github.com/lundybernard/batconf/issues/32)


## Issues

Submit issues, feature requests or bugfixes
on [GitHub](https://github.com/lundybernard/batconf)


## License and Credits

`batconf` is licensed under the 
[MIT license](https://github.com/lundybernard/batconf/blob/main/LICENSE.txt).
and is written and maintained by Lundy Bernard (lundy.bernard@gmail.com)
and Lauren Moore

# Indices and tables

- {ref}`genindex`
