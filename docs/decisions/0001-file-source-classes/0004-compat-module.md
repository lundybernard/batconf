# ADR 0004 — `_compat.py` shared deprecation utility

Date: 2026-05-14
Status: Proposed
Branch: feature/file-sources
Issue: #193

## Context

All three source modules need the same `__getattr__` pattern described in ADR

0003. Duplicating the implementation across `toml.py`, `ini.py`, and
      `yaml.py` would mean three copies of the warning format string,
      stacklevel,
      and `AttributeError` message.

An additional complication: `IniConfig` and `YamlConfig` have different
constructor signatures from their `*Source` replacements, so the name returned
by `__getattr__` is not the same as the display name in the warning message:

- `__getattr__('IniConfig')` → warn `"use 'IniSource' instead"`, but return
  the legacy `_IniConfig` class (which preserves the old `IniConfig` API)
- `__getattr__('TomlConfig')` → warn `"use 'TomlSource' instead"`, and the
  display name and return target are the same (`_TomlConfig`)

## Decision

Add `batconf/sources/_compat.py` with a single public function
`make_deprecated_getattr`. The function is internal (module prefixed with `_`)
and not part of the public API.

```python
def make_deprecated_getattr(
    deprecated: dict[str, str],  # {old_name: display_new_name}
    module_globals: dict,
    module_name: str,
    targets: dict[str, str] | None = None  # {old_name: globals_key_to_return}
):
```

`deprecated` drives the warning message: `"'old_name' is deprecated, use
'display_new_name' instead."`. `targets`, when provided, overrides which key
is looked up in `module_globals` to find the object to return. When omitted,
`display_new_name` is used as the globals key directly.

## Options considered

### Inline `__getattr__` per module

- No shared dependency [pro]
- Three copies of the same logic [con]
- Warning format string may diverge over time [con]

### `_compat.py` (chosen)

- Single implementation; tested once [pro]
- Consistent warning format and stacklevel across all three sources [pro]
- One more internal module [con]

### Public utility function

- Discoverable [pro]
- Deprecation machinery is an implementation detail;
  publishing it sets a maintenance expectation [con]

## Consequences

- `batconf/sources/_compat.py` is an internal module. It must not be imported
  outside the `batconf.sources` package.
- `make_deprecated_getattr` is covered by its own unit tests in
  `batconf/sources/tests/_compat_test.py`.
- Adding a fourth deprecated source in the future requires only a single
  `make_deprecated_getattr` call; no logic needs to be duplicated.
- The `targets` parameter allows the warning message to say `"use 'IniSource'"
  while still returning the legacy `_IniConfig` wrapper class.
