# Zero mandatory external dependencies

Date: 2022-01-01
Status: Accepted

## Context

BatConf's first release bundled `pyyaml` as a hard dependency, since YAML
was the only supported config file format. As INI and TOML support were
added (TOML is in the stdlib as of Python 3.11), the dependency situation
needed to be re-evaluated.

Modern Python applications carry meaningful supply-chain risk from
transitive dependencies. Each additional mandatory package is a potential
security attack vector that every BatConf user inherits, whether or not
they use the feature it provides.

## Decision

The BatConf core package has zero external runtime dependencies. All core
functionality — `Configuration`, `SourceList`, `EnvSource`, `IniSource`,
`TomlSource`, `NamespaceSource`, `DataclassConfig` — relies on the Python
stdlib only. Support for formats that require third-party packages is
provided as optional extras declared in `pyproject.toml`:

- `batconf[yaml]` — adds `pyyaml` for `YamlSource`
- `batconf[toml]` — adds `tomli` for `TomlSource` on Python ≤ 3.10

## Options considered

### Zero mandatory deps, optional extras (chosen)

- Users pay only for what they use [pro]
- No implicit supply-chain risk [pro]
- YAML users must update their dependency declaration [con]
- Slightly more complex install docs [con]

### Bundle all format support

- Single install line; no extras needed [pro]
- All users inherit pyyaml even if they only use INI or TOML [con]
- Future format deps would be forced on all users [con]

### Separate packages (batconf-yaml, etc.)

- Maximum isolation [pro]
- Fragmented ecosystem [con]
- Harder to discover and document [con]

## Rationale

A library with no mandatory dependencies minimizes the risk of supply-chain
attack and maintenance burden. Users who need YAML support opt in explicitly
and document that choice in their own `pyproject.toml`, making the
dependency visible and auditable.

This also means that for projects using only INI or TOML (Python ≥ 3.11),
No packages beyond the stdlib are required.

## Consequences

- `pip install batconf` installs no third-party packages.
- `YamlSource` is gated behind the `yaml` extra; importing it without
  `pyyaml` installed raises an `ImportError`.
- Projects that previously relied on BatConf to pull in `pyyaml` as a
  transitive dependency must add `batconf[yaml]` or `pyyaml` explicitly.
- New format sources that require external packages must be implemented as
  optional extras, not bundled into the core.
