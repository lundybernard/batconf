# ADR 0009 — FileSource class refactor

Branch: feature/file-sources
Issue: #193

`TomlSource`, `IniSource`, and `YamlSource` present one file-source API, and
the legacy `*Config` classes are deprecated. Components 0010–0013 record the
parts of that decision.

| #                                       | Title                                     | Status   |
| --------------------------------------- | ----------------------------------------- | -------- |
| [0010](0010-unified-file-source-api.md) | Unified FileSource API + FileSourceP      | Accepted |
| [0011](0011-lazy-loading.md)            | Lazy file loading via `_raw_data`         | Accepted |
| [0012](0012-import-time-deprecation.md) | Import-time deprecation via `__getattr__` | Accepted |
| [0013](0013-compat-module.md)           | `_compat.py` shared deprecation utility   | Accepted |

See [REQUIREMENTS.md](REQUIREMENTS.md) for the acceptance criteria for this PR.
