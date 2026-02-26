## feedback
The one piece I'd recommend adding to the talk is a comparison
to other similarly aimed tools.

clearly communicate how BatConf is better
than other imperfect solutions currently available,
such as betterconf, ConfZ, BaseSettings, etc.

clear messaging why BatConf would help me to deal with CM
more effectively is critical.
Overall, the abstract is clear, the project in immature.
I think SciPy audience will be happy to give it a try assuming the benefits
are clearly articulated.

configuration management is indeed a common problem,
as illustrated by the rapid adoption of Pydantic settings.


## Notes on comparisons
betterconf:
Both:
* require no additional 3rd party dependencies, only Python's stdlib
* Support user-provided arbitrary configuration sources

Pro betterconf:
* betterconf allows type-casting config values
  BatConf's opinion is that all config values should be treated as strings
  conversion of datatypes should be handled seperately from config loading.
* Less boilerplate, betterconf's Config class creation is a bit more terse
  than BatConf's

Pro BatConf:
* Hierarchical configuration sources: BatConf allows different sources
  (ENV, files, CLI args) partially overwrite lower-ranked sources.
  You can overwrite a value from a config file with an ENV variable, and/or
  a CLI argument.
  It looks like this is *possible* with betterconf, but not simple.
* Distributed config definitions: BatConf config schemas can be built from
  python dataclasses, allowing modules to define their own configuration schemas
  without the need to import anything from BatConf.
* Composability: BatConf's Schemas are designed to be composable from
  sub-modules and 3rd party packages.  If someone provides a config schema for
  Pandas, you will be able to import it, and add it to your application's config


ConfZ:
Both:
* Support Hierarchical configuration sources
* Support user-defined config sources
* Support Nested / Namespaced configurations

Pro ConfZ:
* Typing and checking values using Pydantic.

Pro BatConf:
* Zero required dependencies for supplychain safety.
* Favors composition over inheritance, and avoids tight-coupling
  with your code-base.


OmegaConf:
Both:
* Hierarchical configuration sources (with very different approaches)
* Multiple configuration files for separation of concerns
* Structured configurations using dataclasses
* Dot-notation access for config values

Pro OmegaConf:
* Serialization: save and load configurations to file (planned future feature of BatConf)
* Typed values and type-checking
* Supports more dynamic creation of Configuration objects, such as configs from lists and dicts.
* Variable Interpolation

Pro BatConf:
* Zero required dependencies for supplychain safety (PyYaml is an optional extra)
* Simplicity:
  * Preffers static schemas
  * values as strings (parsing to types is a separate concern)
  * focus on settings which humans interact with, not meta-programming.
* Streamlined Hierarchy of config sources (SourceList, instead of Merging and resolvers)
* Multiple environments (dev, staging, production, etc.) in config files


Dynaconf: https://www.dynaconf.com/

+ include pydantic settings
