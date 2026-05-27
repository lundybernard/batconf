# Source interface: Protocol over ABC

Date: 2021-06-21
Status: Accepted

## Context

Users need a way to implement custom configuration sources.
The interface contract is simple: a single `get(key, path) -> str | None`
method. Two standard Python mechanisms exist for expressing this contract:
`Protocol` (structural subtyping) and abstract base classes (`ABCMeta`).

## Decision

`SourceInterfaceP` (a `Protocol`) is the canonical interface for
configuration sources. Custom sources are not required to inherit from
anything — any class with a conforming `get` method satisfies the
interface.

`SourceInterface` (an `ABCMeta` subclass) also exists as a convenience
for contributors who want explicit ABC enforcement. It is a pragmatic
workaround introduced when mypy had difficulty inferring structural
conformance in certain call sites. It may be removed in a future release
once the underlying type-checker limitations are resolved.

## Options considered

### Protocol only (preferred)

- No forced inheritance [pro]
- Sources remain decoupled from BatConf [pro]
- Structural typing is idiomatic Python [pro]
- Some versions of mypy required explicit inheritance at certain call sites [con]

### ABC only

- Explicit; type checkers have no ambiguity [pro]
- Forces inheritance [con]
- Ties custom source implementations to BatConf internals [con]

### Both (current state)

- Unblocks type checking immediately [pro]
- Existing subclassers are unaffected [pro]
- Two interfaces for the same contract is confusing [con]
- ABC creates implicit coupling [con]

## Rationale

The Protocol captures the intended design: any object with the right
`get` signature is a valid source, regardless of its class hierarchy.
This keeps custom sources loosely coupled and easy to test in isolation.

The `SourceInterface` ABC was added as a pragmatic fix for specific mypy
false positives, not as a deliberate design choice. New custom sources
should implement `SourceInterfaceP` structurally and not subclass
`SourceInterface`.

## Consequences

- `SourceInterfaceP` is the stable public type for type annotations and
  `isinstance` checks.
- `SourceInterface` remains available but is not part of the intended
  long-term API.
- When the type-checker issues are resolved, `SourceInterface` will be
  deprecated and eventually removed.
- Existing code that subclasses `SourceInterface` will continue to work;
  the ABC satisfies the Protocol by structural conformance.
