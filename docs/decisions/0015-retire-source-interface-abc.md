# ADR 0015 — Retire the `SourceInterface` ABC

Date: 2026-08-29
Status: Accepted

## Context

batconf names one source contract twice:

- `SourceInterfaceP`, a `Protocol` in `batconf.sources.types`
- `SourceInterface`, an abstract base class in `batconf.source`

[ADR 0007](0000-foundational/0007-source-interface-protocol-over-abc.md) made
the Protocol canonical and kept the ABC as a workaround for mypy false
positives, to go once the type checker caught up. It set no date. The duality
spread: the file sources declared the Protocol, the environment and namespace
sources subclassed the ABC, and the user guide taught the ABC as the
extension point.

The mypy limitation no longer reproduces. The ABC is public API, so a
workaround that survives the 1.0 freeze becomes a permanent promise.

## Decision

`SourceInterfaceP` is the only source extension point. Every built-in
source declares it. `SourceInterface` emits a `DeprecationWarning` that
names v0.5.0 as its removal version. The guide and the introduction
teach the Protocol only.

Classes that v0.5.0 already removes keep the ABC as their base through
a private alias. Importing them raises no warning for a defect their
users cannot fix.

## Options considered

### Deprecate the ABC, keep `SourceInterfaceP` (chosen)

- One documented extension point before the 1.0 freeze [pro]
- Custom sources need no batconf base class [pro]
- Completes the direction ADR 0007 set [pro]
- Subclasses of the ABC must change before v0.5.0 [con]

### Keep both

- No migration for existing subclasses [pro]
- Freezes a workaround into the 1.0 contract [con]
- Two answers to one question, for every contributor [con]

### Keep the ABC, drop the Protocol

- No ambiguity for type checkers [pro]
- Every third-party source must inherit from batconf [con]
- Reverses ADR 0007 and rewrites every file source [con]

## Rationale

The Protocol states the real contract: batconf calls `get` and nothing
else. Inheritance adds a batconf import to every third-party source and
checks nothing the Protocol does not.

Timing forces the decision now. The deprecation policy deprecates in a
patch release and removes in the next minor. v0.4.1 is the last patch
release before v0.5.0, so the warning ships now or the ABC survives
into 1.0.

The private alias for the deprecated classes avoids churn. Those
classes leave in the same release as the ABC. Migrating them first
would emit warnings that point users at a base class they never chose.

## Consequences

- `from batconf.source import SourceInterface` emits a
  `DeprecationWarning`. The name still resolves, so existing subclasses
  work until v0.5.0.
- Custom sources need no base class. A source that wants type-checker
  enforcement subclasses `SourceInterfaceP`.
- `isinstance` checks against `SourceInterface` move to
  `SourceInterfaceP`, which is `runtime_checkable`.
- v0.5.0 removes `SourceInterface`, the private alias, and the
  deprecated classes that hold it.
