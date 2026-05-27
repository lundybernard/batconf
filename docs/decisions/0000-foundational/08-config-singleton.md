# ConfigSingleton: optional global configuration

Date: 2021-06-21
Status: Accepted

## Context

Many applications want to share a single configuration object across
modules without passing it explicitly through every call site. The
straightforward solution — a module-level global — is convenient but
carries well-known risks: implicit coupling, test pollution, and
difficult-to-reason-about initialization order.

`Configuration` itself is stateless with respect to identity; every call
to `get_config()` produces a fresh object. A separate mechanism is needed
for users who want a shared singleton, without forcing singleton semantics
on users who do not.

## Decision

`ConfigSingleton` is an optional lazy proxy that users may choose to
adopt. It is not required. The intended use case is a single, global
configuration object shared across an application:

```python
# yourmodule/conf.py
CFG = ConfigSingleton(get_config)

# anywhere else in the application
from yourmodule.conf import CFG


value = CFG.some_option
```

Users who adopt `ConfigSingleton` accept the risks inherent in using a
global. Those risks are not hidden; `_reset()` is provided
`_reset()` as an explicit mitigation for the most common consequence:
test pollution.

Key properties:

- **Lazy**: the underlying `Configuration` is not built until first
  attribute access, so import-time side-effects and CLI arg injection
  via `insert_source` are both safe.
- **Reconstructible**: `_reset()` rebuilds the `Configuration` by
  calling the factory again, giving tests a clean slate.
- **Transparent**: all attribute and subscript access is proxied to the
  underlying `Configuration`; `ConfigSingleton` adds no new config API.

## Options considered

### Optional proxy class (chosen)

- Users opt in explicitly [pro]
- `Configuration` stays composable [pro]
- `_reset()` provides test isolation [pro]
- Still a global; test discipline required [con]

### Make `Configuration` a singleton

- Single concept [pro]
- Forces singleton semantics on all users [con]
- Impossible to have two configurations in one process [con]

### No singleton support

- Cleanest design [pro]
- Users reimplement the pattern themselves, often without `_reset()` [con]

### Dependency injection only

- Testable by construction [pro]
- Significant boilerplate for simple applications [con]
- Counter to the target audience [con]

## Rationale

The target audience includes small applications, CLI tools, and
microservices where the ergonomics of `from yourmodule.conf import CFG`
outweigh the risks of a global. Providing `ConfigSingleton` as an
explicit, documented opt-in makes the trade-off visible rather than
leaving users to implement their own globals without the `_reset()`
safety valve.

Keeping `Configuration` free of singleton semantics ensures that
libraries, tests, and multi-configuration scenarios can construct
independent `Configuration` objects without interference.

## Consequences

- `ConfigSingleton` is opt-in. Projects that prefer dependency injection
  or explicit `get_config()` calls at each use site can ignore it
  entirely.
- Users who adopt `ConfigSingleton` are responsible for test isolation.
  The recommended pattern is `CFG._reset()` in `tearDown`.
- `insert_source` works through `ConfigSingleton` via the
  `_HasConfigSources` protocol, so CLI args can be injected after import
  and before first access.
- Two `ConfigSingleton` instances over the same factory are independent
  objects; there is no process-wide enforcement of uniqueness.
