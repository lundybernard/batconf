# ADR 0019 — The INI root section

Date: 2026-09-01
Status: Proposed

## Context

`configparser` has no unnamed section, and `[]` is not a legal header. TOML
and YAML hold root keys natively: with an empty path, both resolve a key
declared on the root schema. INI does not, and the guide documents the
limit.

Child namespaces already resolve in INI, so only keys declared directly on
the root schema lack a home. Once
[an absent path is the root](0017-absent-path-mounts-at-root.md), the empty
path is the ordinary case, and one file format would fail to express a
schema that the other two express. The format would then constrain the
schema.

## Decision

`/ROOT/` is the INI root section. In the `sections` layout it holds the
keys of an empty path. In the `flat` layout it holds the whole file.

```ini
[/ROOT/]
name = demo

[server]
host = localhost
```

The `flat` layout named that section `root`. The name is internal. The loader
adds the `[root]` header itself, and a flat file that also spells it fails
with `DuplicateSectionError`.

The `environments` layout reserves no name. An empty path resolves to the
section of the active environment.

The mapping is INI-only. TOML and YAML keep their native root and receive
no reserved name. In `sections`, the guide documents the reserved name as not
recommended; it exists for parity between the file formats.

No `root_section=` argument ships on any file source.

## Options considered

### A fixed `/ROOT/` section, INI only (chosen)

- `configparser` accepts `/` in a header, so the section parses and holds
  its own keys [pro]
- A path built from Python identifiers never produces the name, so it
  cannot shadow a namespace a user wants [pro]
- The reserved name stays inside the one format that needs it and never
  enters the path vocabulary [pro]
- Section names carry their case and their spacing, so the user sees a near
  miss only through a warning [con]

### A `root_section=` argument

- The project names the section, and no reserved word ships [pro]
- The only reading that keeps a nested namespace inside its project
  prefixes every path the source receives, which reproduces `path=`
  exactly [con]
- The other reading names the root section alone, and leaves nested
  namespaces in sections no project owns [con]
- It is INI-only, so a TOML or YAML project has no matching spelling [con]

### No root section; INI holds no root keys

- The status quo: documented, and no code [pro]
- INI alone cannot express a schema with a root-level key, so the choice of
  file format changes what the schema may declare [con]

### The `[DEFAULT]` section

- `configparser` supplies it, so batconf does not invent a name [pro]
- Its keys inherit into every section, so one root key shadows the same key
  in every namespace [con]
- It never appears in `sections()`, so it is invisible to a reader of the
  file [con]

## Rationale

This is parity, not a recommendation. A project with its own INI file
mounts under its own name and never writes the section. The section exists
so that no schema becomes unreadable purely because the file is INI.

A per-source name for the same namespace was the alternative worth taking
seriously, and it fails on duplication. `path=` is the project-wide mount
point already, and it reaches every source through the frozen
`get(key, path)` parameter that
[ADR 0014](../0014-get-path-parameter.md) settled. A second spelling of the
same namespace, per source and per format, adds a name that the project must
keep in step with the first, and adds no capability.

`/ROOT/` is the only safe fixed literal. `bat` and `conf` are names a user
may legitimately want for a namespace, and `configparser` offers no escape
from the collision. `[DEFAULT]` is worse than a collision: it is a channel
between sections.

The `flat` layout already reserves a section name. That name is internal, so
one spelling of the root across the layouts changes no flat file.

## Consequences

- INI, TOML and YAML agree at the root. A schema with root-level keys reads
  from any of the three.
- `[/ROOT/]` is exact. A header keeps its case and its surrounding
  whitespace, so `[/root/]` and `[ /ROOT/ ]` are other sections, and a near
  miss raises a warning.
- `[DEFAULT]` keys inherit into `/ROOT/`, as they inherit into every other
  section.
- The guide documents the section as format parity and directs a project
  with a dedicated INI file to mount under its own name instead.
- In a shared file, `[/ROOT/]` belongs to no project, exactly as the file
  root does. See
  [the format and environment contract](0021-format-environment-contract.md).
- No file source gains a namespace argument. `path=` stays the one mount
  point.
