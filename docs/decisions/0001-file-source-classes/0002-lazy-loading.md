# ADR 0002 — Lazy file loading via `_raw_data`

Date: 2026-05-14
Status: Proposed
Branch: feature/file-sources
Issue: #193

## Context

The v0.4.x `*Config` classes call the file loader in `__init__`, which
causes two problems:

1. **Testing friction.** Tests that need to inject a known dict must patch the
   loader function before constructing the object. The patch target differs
   across the three classes.
2. **Inconsistent `missing_file_option` semantics.** With eager loading, a
   `missing_file_option='error'` source raises `FileNotFoundError` at
   construction time. A `missing_file_option='warn'` source logs at
   construction time. Users cannot construct the object first and defer the
   I/O failure to the first `.get()` call.

`IniSource` introduced a partial workaround: a `try/except AttributeError`
guard in the `_data` property delays the load until first access but is not
consistent with the other two sources.

## Decision

Move file I/O out of `__init__` into a `cached_property` named `_raw_data`.
Derive the caller-visible view in a plain `@property` named `_data`:

```
__init__    stores path, format, options — no I/O
_raw_data   cached_property — reads file on first access, caches result
_config_env property with setter — resolved from _raw_data on first _data access
            when not set by the caller
_data       property — slices _raw_data by config_env (environments format)
            or returns _raw_data as-is (sections / flat)
```

Test injection uses `cached_property`'s storage contract — setting a value
directly in `__dict__` bypasses computation:

```python
ts = TomlSource(file_path='irrelevant.toml')
ts.__dict__['_raw_data'] = {'my_env': {'key': 'value'}}
ts._config_env = 'my_env'
assert ts._data == {'key': 'value'}   # no file read
```

## Options considered

### Eager load in `__init__` (status quo)

- Simple; object is fully populated after construction [pro]
- Ties construction to I/O [con]
- Injection-based tests require patching the loader function [con]

### `try/except AttributeError` in property (`IniSource` approach)

- Lazy; no extra import needed [pro]
- Relies on catching `AttributeError` for normal control flow [con]
- Not self-documenting [con]
- Not consistent across sources [con]

### `cached_property` (chosen)

- Standard library; intent is obvious [pro]
- Test injection via `__dict__` is a documented pattern [pro]
- Consistent across all three sources [pro]
- Requires the class not to define `__slots__` [con]

## Consequences

- No file I/O on construction; the first `.get()` or `._data` access triggers
  the load.
- `missing_file_option='error'` raises `FileNotFoundError` on first value
  access, not at construction time.
- Unit tests inject data via `obj.__dict__['_raw_data'] = {...}` without
  patching loader functions.
- `_config_env` is `None` after `__init__` when not provided by the caller;
  it is populated from the file's `batconf.default_env` key on first `_data`
  access (environments format only).
