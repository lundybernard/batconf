# ADR 0003 — Import-time deprecation via module `__getattr__`

Date: 2026-05-14
Status: Proposed
Branch: feature/file-sources
Issue: #193

## Context

`TomlConfig`, `IniConfig`, and `YamlConfig` must be deprecated without
breaking code that still uses them. Two questions arise:

1. **When should the warning fire?** At instantiation or at import?
2. **How do we remove the name from the module without changing the class?**

The v0.4.x initial deprecation implementation used `warnings.warn` inside
`__init__` (instantiation-time). This approach has two drawbacks: the warning
fires late (buried inside call stacks, not at the `import` line), and it is
silenced after the first occurrence per call site by Python's default `once`
filter — so code that creates many instances only warns once in an
unpredictable location.

## Decision

### Warning timing — import-time via module `__getattr__`

Python calls a module's `__getattr__` only when the requested name is absent
from the module's `__dict__`. Assigning a `__getattr__` function and removing
the old name from globals causes the warning to fire on any attribute access —
including `from batconf.sources.toml import TomlConfig` — making the
deprecated name visible immediately in `import` statements that are easy to
find and fix.

### Class identity — `del` rather than rename

To trigger `__getattr__`, the class name must not be in the module's
`__dict__`. Two approaches:

| Approach                                   | Effect on `cls.__name__`   | Effect on repr / pickle                                  |
| ------------------------------------------ | -------------------------- | -------------------------------------------------------- |
| `class _TomlConfig(TomlSource)`            | `'_TomlConfig'`            | repr and pickle change; existing pickled instances break |
| `_TomlConfig = TomlConfig; del TomlConfig` | `'TomlConfig'` (unchanged) | No change to repr or pickle                              |

The `del` approach is chosen. The class definition is left untouched; the
public name is removed from globals after a private reference is saved:

```python
class TomlConfig(TomlSource): ...   # __name__ = 'TomlConfig'

_TomlConfig = TomlConfig            # save before deletion
del TomlConfig                      # not in __dict__ → __getattr__ fires

__getattr__ = make_deprecated_getattr(
    deprecated={'TomlConfig': 'TomlSource'},   # display name in warning
    module_globals=globals(),
    module_name=__name__,
    targets={'TomlConfig': '_TomlConfig'},      # object to return
)
```

## Options considered

### `warnings.warn` in `__init__`

- `cls.__name__` unchanged [pro]
- Warning fires at instantiation, not import [con]
- Silenced after first hit per call site by Python's default filter [con]

### `class _TomlConfig` + `__getattr__`

- Warning fires at import [pro]
- `cls.__name__` becomes `'_TomlConfig'` [con]
- Breaks repr and pickle [con]

### `del TomlConfig` + `__getattr__` (chosen)

- Warning fires at import [pro]
- `cls.__name__` unchanged [pro]
- No side effects on the class object [pro]

## Consequences

- `from batconf.sources.toml import TomlConfig` emits `DeprecationWarning`;
  `toml.TomlConfig` does the same.
- `TomlConfig.__name__` remains `'TomlConfig'`; repr and pickle are unaffected.
- `isinstance(tc, TomlConfig)` is not directly possible after import since
  `TomlConfig` is no longer a module-level name. Users should migrate to
  `isinstance(tc, TomlSource)`.
- The deprecated classes are removed in v0.5.0.
