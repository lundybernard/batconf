# Module path as default namespace

Date: 2021-06-21
Status: Accepted

## Context

Config keys must be namespaced to avoid collisions when multiple modules
contribute configuration to the same `SourceList`. A convention is needed
for how a config class maps to a section in a config file or an ENV
variable prefix.

## Decision

`Configuration` derives the root namespace for a config class from
`config_class.__module__` when no explicit `path` is provided. Config
file sections and ENV variable prefixes mirror the Python dotted module
path.

An explicit `path` parameter was added to `Configuration.__init__` (and
the recommended `get_config` function signature) to allow callers to
override the default.

## Options considered

### `__module__` default (chosen)

- Zero configuration needed [pro]
- Works out of the box for single-module projects [pro]
- Config file structure is coupled to module layout [con]
- Renaming a module requires updating config files [con]

### Explicit mandatory path

- Decoupled from module layout from day one [pro]
- Every `Configuration` construction requires a path argument [con]
- More boilerplate for simple projects [con]

### Flat (no namespace)

- Simplest file format [pro]
- Key collisions across modules [con]
- Unworkable for multi-module projects [con]

## Rationale

Deriving the namespace from `__module__` was the original default: it
required no configuration and worked for simple single-application projects
where the config structure happened to mirror the module tree.

During development it became clear that tying config file
structure to module layout is a design constraint, not a feature. A
`SqlClient` config section should not be named by whichever package the
class lives in — that section name belongs to the config schema, not the
source tree. Renaming or moving a module should not require updating config
files.

The explicit `path=` parameter was added to decouple namespace from module
layout and is the recommended approach for any project where config
structure needs to be stable and independent of module paths. The
`__module__` default is retained for backwards compatibility, not as the
preferred style.

## Consequences

- Config file sections use dotted Python module paths
  (e.g. `[dev.yourproject.example.client]`).
- ENV variable names use the uppercased, underscore-joined path
  (e.g. `YOURPROJECT_EXAMPLE_CLIENT_HOST`).
- Renaming a Python module changes the default namespace and breaks
  existing config files unless `path=` is used to pin it.
- Sub-`Configuration` objects compute their path by appending the field
  name to the parent path, so the tree structure always mirrors the
  dataclass nesting.
