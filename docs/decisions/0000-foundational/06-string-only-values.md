# String-only config values

Date: 2021-06-21
Status: Accepted

## Context

BatConf sources are heterogeneous: CLI args, environment variables, INI
files, TOML files, YAML files, and arbitrary user-defined sources. Each
source has different native type capabilities. Environment variables, for
example, can only store strings. A contract is needed for what a source's
`get()` method may return.

## Decision

Every source's `get(key, path)` method must return `str | None`. `None`
(and all other falsey values) signals "this source does not have a value
for this key." Values are not coerced, parsed, or validated; callers receive the raw
string and are responsible for converting it.

This contract is expressed in `SourceInterfaceP`:

```python
class SourceInterfaceP(Protocol):
    def get(self, key: str, path: str | None = None) -> str | None: ...
```

## Options considered

### `str | None` only (chosen)

- Sources are interchangeable [pro]
- No type-mismatch bugs across sources [pro]
- ENV vars are a first-class source [pro]
- Callers must cast; `int("8080")` is boilerplate for numeric values [con]

### `Any | None`

- Sources can return rich types from YAML/TOML [pro]
- ENV source can never match [con]
- Two sources for the same key may return different types [con]
- Comparison logic becomes undefined [con]

### Typed values with coercion

- Callers receive ready-to-use values [pro]
- Requires a schema with declared types (e.g. Pydantic) [con]
- Coercion failures raise at read time [con]
- Significantly more complex [con]

## Rationale

Environment variables are a core supported source (tier-2 in the
12-factor priority chain) and can only store strings. Requiring all
sources to conform to `str | None` ensures that any value retrievable
from ENV is also retrievable from any other source with identical
semantics. This eliminates a whole class of bugs where a config value
works in one environment (reads from a typed TOML file) but fails in
another (reads from ENV as a string).

Type conversion is a concern for the application layer, not the
configuration layer.

## Consequences

- `SourceInterfaceP.get` is typed `-> str | None`.
- Falsey non-string values (`False`, `0`, `""`) returned by a source are
  treated as missing and cause the next source in `SourceList` to be tried.
  If a config key genuinely needs a falsey value, it must be stored as
  `"false"`, `"0"`, or `"none"` and the caller interprets it.
- User-defined sources that return non-string types (e.g. a dict-backed
  source returning an integer) will cause silent type errors at the call
  site. The contract is documented but not enforced at runtime.
