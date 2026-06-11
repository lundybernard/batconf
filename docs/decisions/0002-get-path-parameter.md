# ADR 0002 — Standardize `.get()` on `path`; deprecate the `module` keyword

Date: 2026-06-03
Status: Proposed
Branch: feature/get-name-resolution
Issue: #3

## Context

Every configuration source implements
`get(self, key, <namespace>) -> str | None`, where the second argument is the
dotted namespace the key lives under. The canonical interface,
`SourceInterfaceP` (`batconf/sources/types.py`), names that argument **`path`**.
The concrete sources disagree:

- **`path`** (matches the Protocol): `SourceList`, the `SourceInterface` ABC,
  `IniSource`, `TomlSource`, `YamlSource`
- **`module`** (diverges): `DataclassConfig`,
  `NamespaceConfig`/`NamespaceSource`, `EnvConfig`/`EnvSource`,
  `CliArgsConfig` (deprecated), and the legacy `YamlConfig` (deprecated)

The name `module` is a historical artifact: namespaces were originally derived
from a config class's `__module__`. They are now arbitrary dotted paths, so
`path` describes the argument accurately and `module` is misleading. The split
also means a caller cannot rely on one keyword name across sources.

Issue #3 originally proposed going further — removing the second argument
entirely and folding it into the `key` as a single dotted lookup,
`get("project.database.host")`. That is **rejected** here: every source would
then have to split, re-join, and strip the root namespace from one string
(`DataclassConfig` already carries asymmetric root-strip logic between its two
branches), pushing string-math into each implementation. Keeping an explicit
`path` channel is simpler and keeps the namespace separate from the key.

## Decision

`path` is the one canonical second parameter for every source `.get()`.

Three **live** sources currently expose `module`: `DataclassConfig`,
`NamespaceConfig`/`NamespaceSource`, and `EnvConfig`/`EnvSource`. Each renames
the parameter to `path` and accepts `module` as a **deprecated optional
argument** for one release cycle:

```python
def get(self, key: str, path: str | None = None, module: str | None = None):
    path = deprecated_module(path, module)
    ...
```

`module` is a plain trailing optional argument, not keyword-only (`*, module`):
nothing passes a third positional argument, so the marker would buy nothing.

A shared helper, `deprecated_module(path, module)` in
`batconf/sources/_compat.py`, emits the warning — one message, one v0.5.0
removal point — and falls back to `module` only when `path` was not given.

The two **already-deprecated** classes that also expose `module` —
`CliArgsConfig` and the legacy `YamlConfig` — are left untouched. Each already
emits a `DeprecationWarning` before `.get()` is ever reached (`YamlConfig` at
import via the ADR 0003 module-`__getattr__` mechanism; `CliArgsConfig` at
construction), and both are removed in v0.5.0. Adding a second
`module`-keyword warning to their `.get()` would be redundant noise on names
that are disappearing anyway.

The six sources already on `path` are untouched. The `module` keyword is
removed entirely in **v0.5.0**, at which point every live signature is
`get(self, key, path=None)`.

## Options considered

### Deprecated `module` argument on the 3 live diverging sources (chosen)

- Smallest diff; only the live sources that misnamed the argument change,
  and already-deprecated classes are left alone [pro]
- Positional 2nd argument is `path` everywhere immediately [pro]
- Deprecated `module` keyword stays visible to mypy and IDEs [pro]
- No string-math added to any source [pro]
- Signatures are not byte-identical until v0.5.0 — the 3 live sources carry
  an extra optional `module` argument during the deprecation cycle [con]

### `module` keyword-only on all sources

- Byte-identical signatures across every source [pro]
- `module=` warns no matter which source is called [pro]
- Adds a deprecated argument to sources that never advertised `module`,
  for no caller benefit [con]
- Larger diff [con]

### Absorb `module` via `**kwargs`

- Cleanest visible signature, `(key, path)` [pro]
- Deprecated argument is invisible to introspection and autocomplete [con]
- Weaker typing [con]

### Collapse into a single dotted `key` (Issue #3 as written)

- One argument total [pro]
- Forces split / re-join / root-strip string-math into every source [con]
- More code and more edge cases per source [con]

## Consequences

- Passing `module=` to `EnvSource`, `NamespaceSource`, or `DataclassConfig`
  `.get()` emits `DeprecationWarning`; passing `path=` or the positional 2nd
  argument does not warn.
- `CliArgsConfig` and `YamlConfig` `.get()` keep their `module` parameter
  silently — both classes already warn elsewhere and are removed in v0.5.0.
- Tests that call `.get(..., module=...)` on the live sources (`env_test`,
  `dataclass_test`, `argparse_test`) move to `path=` or assert the warning.
  The deprecated-class tests (`args_test`, `yaml_test`) are unaffected.
- `SourceInterfaceP` is unchanged — it already declares `path`. The Protocol
  intentionally omits a default value: downstream implementors may require
  `path` explicitly, and adding a default to the Protocol would cause a mypy
  error on those implementations. The asymmetry is harmless — an
  implementation with `path=None` satisfies a Protocol that marks `path`
  required, but not the reverse.
- v0.5.0 removes the `module` keyword and the helper, leaving
  `get(self, key, path=None)` on every live source. Tracked as a follow-up to
  Issue #3.
