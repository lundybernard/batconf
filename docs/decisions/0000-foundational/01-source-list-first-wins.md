# SourceList first-wins priority

Date: 2021-06-21
Status: Accepted

## Context

Multiple configuration sources are supported: CLI args, environment
variables, config files, and dataclass defaults. A strategy is needed to
resolve conflicts when the same key is present in more than one source.

Designed explicitly for 12-factor applications, where the
prescribed priority order is: process arguments > environment variables >
config file > application defaults.

## Decision

`SourceList` holds an ordered sequence of sources and queries them in
index order. The first source that returns a non-`None` value wins; the
remaining sources are not consulted for that key. Sources can be added
at any position at runtime via `SourceList.insert_source`.

The canonical priority order is:

1. CLI arguments (`NamespaceSource`)
2. Environment variables (`EnvSource`)
3. Config file (`IniSource`, `TomlSource`, `YamlSource`, or custom)
4. Dataclass defaults (implicit; returned by `Configuration` when all
   sources return `None`)

## Options considered

### Ordered first-wins (chosen)

- Predictable; matches 12-factor priority order [pro]
- Easy to reason about overrides [pro]
- Dynamic insertion via `insert_source` is straightforward [pro]
- A lower-priority source can never partially override a higher-priority one [con]

### Deep-merge all sources

- Allows partial overrides at any level [pro]
- Complex merge semantics [con]
- Behaviour with missing keys is ambiguous [con]
- Hard to trace which source contributed a value [con]

### Last-wins

- Simple implementation [pro]
- Inverts 12-factor order [con]
- CLI args must be appended last, which is counter-intuitive [con]

### Per-key priority rules

- Fine-grained control [pro]
- Significant complexity [con]
- No clear use case [con]

## Rationale

First-wins is the simplest strategy that satisfies 12-factor design
and is easy to explain: "earlier in the list = higher priority." It maps
directly onto the mental model users already have from the 12-factor app spec
(env overrides file; CLI overrides env).

Dynamic insertion (`insert_source`) lets CLI args be parsed and injected
after the initial `SourceList` is constructed — a common pattern where
`get_config()` is called at import time and CLI args are not yet available.

## Consequences

- `SourceList` is the only object that knows the priority order; `Configuration`
  and all sources are unaware of each other.
- `None` and all other falsey values (`""`, `False`, `0`) are treated as
  "not found" and cause the next source to be tried. This means falsey
  non-string values cannot be stored as real config values.
- New sources can be inserted at runtime without rebuilding the
  `Configuration` object.
- The default priority order matches 12-factor but is not enforced;
  callers can construct any order they need.
