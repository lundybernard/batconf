# ADR 0018 — A caller-declared environment-variable prefix

Date: 2026-09-01
Status: Proposed

## Context

`EnvSource` takes a `prefix` argument. An undeclared prefix keeps the 0.4.0
rule: `BAT` leads the variable name when the path is empty, and no prefix
applies otherwise. That `BAT` is a stand-in for a missing path, not a
namespace. With `prefix=None`, no prefix applies, and an empty path reads
the bare name.

Once [an absent path is the root](0017-absent-path-mounts-at-root.md), the
empty path is the ordinary case, not the exception. A root-level key then
resolves to a bare uppercase name: `NAME`, `PATH`, `HOME`, `USER`. Those
are ambient process variables. The failure is silent, and the shell that
started the process decides it: the lookup returns a value the user never
set for this program, and an unset variable and a foreign variable are
indistinguishable in the result.

A near-root namespace collides as easily as the root. A `server` namespace
holding `host` resolves to `SERVER_HOST` with no prefix.

No batconf-owned environment variable exists yet, so batconf can reserve a
namespace at no cost to any user. A reservation made after 1.0 displaces
whatever a user already keeps under that name, and is itself a documented
behaviour change.

## Decision

`EnvSource` gains a `prefix` argument. The prefix applies to every lookup,
not to the root alone. An undeclared prefix keeps the `BAT` behaviour and
warns; `None` declares no namespace. The hardcoded `BAT` prefix is
deprecated in 0.4.1 and removed in 0.5.0. `prefix` itself lands in 0.4.1
alongside the deprecation.

From 0.5.0, with `prefix=None` and an empty path, a lookup returns `None`.
`EnvSource` never reads a bare single-word name by accident. In 0.4.1, that
lookup reads the bare name.

From 0.5.0, `EnvSource(raw=True)` enables bare-name resolution. The guide
documents it as raw environment access: schema-declared fields read ambient
variables, and the collision risk is the caller's chosen trade. In 0.4.1,
`EnvSource` has no `raw` parameter.

The `BATCONF_*` namespace is reserved. User values must not live there, and
no source serves a user lookup from it.

## Options considered

### An optional prefix, no default, bare names behind `raw=True` (chosen)

- The environment namespace is the project's own name, chosen by the
  project [pro]
- An unprefixed root cannot read an ambient variable by accident [pro]
- Raw access stays available, and the call site shows the trade [pro]
- A project states its name on every `EnvSource` it builds [con]

### Keep the hardcoded `BAT` prefix

- Nothing to migrate [pro]
- Puts a framework name in every user's variables [con]
- Applies only at the root, so it namespaces nothing below it [con]

### No prefix, and resolve bare names at the root

- Shortest variable names, and nothing to configure [pro]
- A schema field named `path`, `home` or `user` reads an ambient
  variable [con]
- The failure is silent, and it depends on the shell rather than on the
  configuration [con]

## Rationale

The prefix is a prerequisite for the root mount, not a convenience. The
module name was doing this work by accident; removing it without a
replacement leaves root and near-root lookups in the shared namespace of
the process.

Refusing rather than reading is the point of the default. A wrong value
from the ambient environment looks the same as a value the user meant, and
it wins over the config file. Returning `None` makes the schema default
apply instead, which is the behaviour a caller who declared no namespace
can reason about. `raw=True` keeps the capability and puts the risk where a
reader sees it.

The prefix is mandatory by documentation, not by signature. A required
argument would remove a working signature and buy nothing over having no
default.

## Consequences

- A project that reads environment variables picks a prefix and states it
  on each `EnvSource`. `BAT` warns from 0.4.1 and is gone in 0.5.0.
- A project must not choose `batconf` as its prefix. That name is reserved.
- The underscore join is not injective. Prefix `alpha` with path `server`
  and prefix `alpha_server` with no path both produce `ALPHA_SERVER_HOST`.
  The hazard exists today; a caller-chosen prefix enlarges it, because the
  caller picks the colliding name.
- The missing-value message composes an environment variable name itself.
  It must name the variable the source would read, or it directs the user
  to a name that has no effect.
- The bootstrap pattern reads the reserved namespace through
  `EnvSource(prefix='batconf')`. `raw=True` is not that reader: with no
  prefix it resolves a bare name, which sits outside the namespace.
  See [environment selection](0020-environment-selection-bootstrap.md).
