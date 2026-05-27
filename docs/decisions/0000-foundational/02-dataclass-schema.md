# Dataclass as config schema

Date: 2021-06-21
Status: Accepted

## Context

Users need a way to declare their configuration structure:
what keys exist, how they are nested, and what defaults apply. Several
approaches were available.

## Decision

Use Python's stdlib `dataclass` as the config schema type. Config classes
are plain dataclasses: no BatConf base class, no BatConf decorator, no
BatConf import required in the file that defines them. The schema is a
tree of nested dataclasses; each nested dataclass becomes a sub-namespace
in the resolved `Configuration`.

## Options considered

### stdlib `dataclass` (chosen)

- No BatConf imports required in schema files [pro]
- Schema usable without BatConf [pro]
- Nesting via composition [pro]
- Requires `ConfigP` protocol check rather than `isinstance(x, BatConfBase)` [con]

### BatConf-specific base class

- Explicit type hierarchy [pro]
- `isinstance` checks are trivial [pro]
- Every schema file must import from BatConf [con]
- Tight coupling makes adoption and refactoring harder [con]

### TypedDict

- Familiar to users of typed dicts [pro]
- No default values [con]
- No nesting via composition [con]
- Requires a separate default mechanism [con]

### Pydantic / attrs model

- Rich validation [pro]
- Coercion built-in [pro]
- External dependency [con]
- Validation semantics conflict with BatConf's string-only value contract [con]

## Rationale

Using stdlib `dataclass` keeps BatConf non-intrusive. A module's config
class can be defined, tested, and used as a plain data object independently.
This makes adoption incremental — a team can add BatConf to an existing
project by writing a single `conf.py` without touching any existing module
files. Config classes can also be factored out or moved between projects
without pulling BatConf along.

Defaults declared on the dataclass fields serve as the final fallback values
in the priority chain, at zero extra cost.

## Consequences

- `batconf.types.ConfigP` is a structural `Protocol` (not a base class)
  that detects config classes via `__dataclass_fields__`.
- All batconf imports can be isolated to a single `conf.py` per module.
- Config dataclasses are usable as plain objects in tests and in code that
  does not use BatConf at all.
- Validation and type coercion are out of scope; callers are responsible
  for converting string values to the types they need.
