# FileSource Class Refactor — Requirements

> Author: Lundy Bernard
> Date: 2026-05-14
> Branch: feature/file-sources
> Issue: #193

---

## Purpose

Replace the three legacy file-backed configuration classes (`TomlConfig`,
`IniConfig`, `YamlConfig`) with a unified set of `*Source` classes that share
a common interface, load files lazily, and deprecate the old names with
import-time warnings.

---

## Requirements

### R1 — Unified constructor signature

All three file source classes must accept the same four keyword arguments in
the same order: `file_path`, `file_format`, `config_env`,
`missing_file_option`. Callers must be able to swap sources without changing
call sites.

### R2 — Structural protocol

A `FileSourceP` Protocol must be the canonical type for file source objects.
The Protocol must be checkable with `isinstance` and usable as a type
annotation. No concrete inheritance from a base class is required.

### R3 — Lazy file loading

No file I/O at construction time. The file must be read on the first access
of a value, not in `__init__`. A `missing_file_option='error'` source must
not raise until a `.get()` is called.

### R4 — Consistent `missing_file_option` behaviour

All three sources must support `'warn'`, `'ignore'`, and `'error'` options
with identical semantics. The behaviour must be exercised by parity integration
tests that run the same assertions against all three source classes.

### R5 — Deprecation warnings on import

`TomlConfig`, `IniConfig`, and `YamlConfig` must remain importable for one
release cycle but emit a `DeprecationWarning` when the name is accessed from
the module. The warning must fire on `from batconf.sources.x import XxxConfig`,
not on instantiation.

### R6 — Preserved class identity

The deprecated classes must retain their original `__name__` values so that
existing `repr()` output, error messages, and any pickled instances are
unaffected.

### R7 — Test parity

Integration tests must verify that `TomlSource`, `IniSource`, and `YamlSource`
return identical values for the same logical key from equivalent `environments`,
`sections`, and `flat` config files.

### R8 — No regressions

All existing tests that exercise the old `*Config` classes must continue to
pass (with warnings suppressed where needed). No public API other than the
deprecated names may be removed.

---

## Success criteria

- `FileSourceP`, `TomlSource`, `IniSource`, `YamlSource` are exported from
  `batconf`
- `from batconf.sources.toml import TomlConfig` emits `DeprecationWarning`;
  the returned object is a subclass of `TomlSource`
- `TomlConfig.__name__ == 'TomlConfig'` (and equivalently for Ini/Yaml)
- `TomlSource(file_path='missing.toml')` raises no exception; first `.get()`
  on a `missing_file_option='error'` source raises `FileNotFoundError`
- All parity integration tests pass for all three sources across all three
  file formats
- CI green on the final commit
