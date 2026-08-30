# FileSource Class Refactor (4 decisions)

Branch: feature/file-sources
Issue: #193

Four decisions made during the introduction of `TomlSource`, `IniSource`, and
`YamlSource` and the deprecation of the legacy `*Config` classes.

| #                                       | Title                                     | Status   |
| --------------------------------------- | ----------------------------------------- | -------- |
| [0001](0001-unified-file-source-api.md) | Unified FileSource API + FileSourceP      | Accepted |
| [0002](0002-lazy-loading.md)            | Lazy file loading via `_raw_data`         | Accepted |
| [0003](0003-import-time-deprecation.md) | Import-time deprecation via `__getattr__` | Accepted |
| [0004](0004-compat-module.md)           | `_compat.py` shared deprecation utility   | Accepted |

See [REQUIREMENTS.md](REQUIREMENTS.md) for the acceptance criteria for this PR.
