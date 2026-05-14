# ADR 0001 — Unified FileSource API

Date: 2026-05-14
Status: Proposed
Branch: feature/file-sources
Issue: #193

## Context

batconf v0.4.x ships three file-backed configuration sources with inconsistent
constructor signatures:

| Class        | `file_path` param  | env param                        | format param                       |
|--------------|--------------------|----------------------------------|------------------------------------|
| `TomlConfig` | `file_path`        | `config_env: str\|None`          | `file_format`                      |
| `IniConfig`  | `file_path`        | `config_env: _EnvOpts` (2nd pos) | `file_format` (4th, after env)     |
| `YamlConfig` | `config_file_name` | `config_env: str\|None`          | `enable_config_environments: bool` |

Callers cannot swap one source for another without updating call sites, and
no shared type exists for type annotations or `isinstance` checks.

## Decision

Introduce three new classes — `TomlSource`, `IniSource`, `YamlSource` — all
conforming to a shared `FileSourceP` Protocol:

```python
class FileSourceP(Protocol):
    def __init__(
        self,
        file_path: str,
        file_format: Literal[
            'environments', 'sections', 'flat'] = 'environments',
        config_env: str | None = None,
        missing_file_option: Literal['warn', 'ignore', 'error'] = 'warn',
    ): ...

    def get(self, key: str, path: str | None = None) -> str | None: ...

    def keys(self): ...
```

The `file_format` argument replaces `enable_config_environments` and makes the
three modes explicit: `'environments'` (multi-env config with a default
declared in the file), `'sections'` (top-level sections as namespaces), and
`'flat'` (all keys at root level).

## Options considered

### Shared ABC base class

- Forces subclasses to implement the interface [pro]
- Requires inheritance [con]
- `IniSource` stores a `ConfigParser`, not a plain dict;
  a shared base class would need empty stubs or overrides for every method [con]

### Protocol (chosen)

- Structural typing; no forced inheritance [pro]
- `isinstance` check available via `runtime_checkable` [pro]
- Slightly less familiar than ABCs for contributors new to Protocol [con]

### Leave signatures unchanged

- No migration cost [pro]
- Callers cannot treat the three sources interchangeably [con]
- Type annotations impossible without a union type [con]

## Rationale

`IniSource` stores a `ConfigParser` rather than a `dict[str, Any]`, so its
internal structure differs from `TomlSource` and `YamlSource`. A shared base
class would either expose implementation details or force empty method stubs.
A Protocol captures the public contract without constraining the internals.

## Consequences

- `TomlSource`, `IniSource`, `YamlSource` are the canonical file source
  classes going forward.
- `from batconf import TomlSource, IniSource, YamlSource` works from v0.4.x.
- `FileSourceP` is the stable structural type for type annotations.
- `file_format='environments'` replaces the `enable_config_environments=True`
  boolean; `'sections'` replaces `enable_config_environments=False`.
- Old `*Config` classes are deprecated but remain usable; see ADR 0003.
