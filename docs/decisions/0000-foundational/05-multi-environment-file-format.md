# Multi-environment config file format

Date: 2021-06-21
Status: Accepted

## Context

Config files need to support multiple deployment environments (dev, staging,
prod) without requiring separate files per environment. The file source must
know which section to read from, and there must be a way to declare a
default environment so that the file works out of the box with no extra
arguments.

Config keys are already namespaced by dotted module path (see
[module-path-namespace](04-module-path-namespace.md)), so the section
naming convention must compose with that path.

## Decision

The default file format (`file_format='environments'`) prefixes every
section with an environment name:

```ini
[batconf]
default_env = dev

[dev.yourproject.example.client]
host = localhost

[prod.yourproject.example.client]
host = 192.168.1.1
```

The active environment is resolved in this order:
1. The `config_env` argument passed to the source constructor.
2. The `default_env` key in the `[batconf]` section of the file.
3. No environment prefix (flat lookup) if neither is set.

Two additional formats are supported for simpler use cases:
- `'sections'` — sections use the dotted config path directly, no environment prefix.
- `'flat'` — a single flat key/value file with no sections.

All three file sources (`IniSource`, `TomlSource`, `YamlSource`) implement
the same three formats with identical semantics.

## Options considered

### Env-prefixed sections, default in file (chosen)

- Single file covers all environments [pro]
- Default env declared alongside config; self-contained [pro]
- Switching env requires only one argument [pro]
- INI requires empty intermediate parent sections [con]

### Separate file per environment

- Simple file structure [pro]
- File-selection logic must live outside BatConf [con]
- Values shared across envs must be duplicated or inherited separately [con]

### Environment as a top-level key in a nested format

- Natural in YAML/TOML [pro]
- Does not translate to INI [con]
- Inconsistent across formats [con]

### ENV variable selects the file

- Environment selection driven by deploy infrastructure [pro]
- No in-file default needed [pro]
- No single-file multi-env story [con]
- Duplication across files [con]

## Rationale

A single file that covers all environments is easier to review and diff
than a directory of per-environment files. Prefixing sections with the
environment name keeps the structure visible and explicit — every section
declares which environment it belongs to.

Declaring `default_env` inside the file means the file is self-contained:
a developer can clone the repo and run the project without setting any
environment variables — the default is declared in the file itself.

## Consequences

- All three file sources share the same `file_format` parameter and the
  same three format modes, so users can switch formats by changing the
  source class without changing the file format argument.
- INI files in `environments` mode require empty intermediate sections
  (`[dev]`, `[dev.yourproject]`) due to INI parser constraints; TOML and
  YAML do not have this requirement.
- `config_env` can be passed at construction time (e.g. read from an ENV
  variable) to override the `default_env` declared in the file.
