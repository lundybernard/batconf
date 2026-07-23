# Comparing BatConf to Other Tools

Python has many configuration libraries, and BatConf is not the right
choice for every project. This page compares BatConf to the most widely
adopted alternatives, so you can decide whether BatConf fits your
project — or whether another tool is a better match.

The comparison is based on a review of each project's official
documentation (July 2026). If you spot an error or an outdated claim,
please [open an issue](https://github.com/lundybernard/batconf/issues).

## BatConf's scope and philosophy

Understanding what BatConf deliberately does — and does not — do makes
the comparison below much easier to read.

- **Layered source composition.** Configuration is composed from
  multiple sources with a clear precedence. The default order is
  CLI args > environment variables > config file > dataclass defaults,
  and the order is fully customizable via the `SourceList`.
- **Plain dataclasses, zero required dependencies.** Config schemas are
  standard-library dataclasses. The core package installs nothing else;
  YAML support is an optional extra (`batconf[yaml]`), TOML uses the
  stdlib `tomllib` on Python 3.11+, and INI needs only the stdlib.
- **Explicit CLI integration.** Your application owns its `argparse`
  parser; the parsed `Namespace` is handed to BatConf as a config
  source. BatConf never parses `argv` itself and never takes over your
  entry point.
- **An ergonomic Configuration object.** Values are read via attribute
  dot-paths (`cfg.service.host`) or subscript access (`cfg['key']`),
  the latter enabling dynamic lookups like `cfg.clients[client_id]`.
- **Validation is a separate concern.** BatConf organizes configuration
  sources and provides access to their values. Input validation belongs
  in your application, scoped to its actual needs — most small apps,
  developer tools, and automation scripts do not need exhaustive
  validation of safe, user-controlled config values, and BatConf will
  not lock you into a validation library. If you want validation
  bundled into the config layer, that is a perfectly valid choice —
  pick an all-in-one tool like pydantic-settings.
- **Configuration is not data.** BatConf handles the *human interface*
  of application configuration. It is not a data-ingestion tool, and it
  does not try to be one; some tools below blur that line by design.
- **Non-intrusive by principle.** BatConf imports can be isolated to a
  single source file, so it does not sprawl through a codebase or
  create lock-in.

BatConf's primary audience is small applications, developer and
automation tooling, and scientific-Python projects that want clean,
layered config composition without a framework taking over.

## Feature comparison

| Tool | Config sources | Layering / precedence | Validation / typing | CLI support |
|---|---|---|---|---|
| **BatConf** | CLI args, env vars, YAML/TOML/INI files, dataclass defaults; custom sources via protocol | Default: CLI > env > files > defaults; order customizable via `SourceList` | Dataclasses + type hints; validation deliberately out of scope — bring your own | Explicit: wraps your app's own argparse `Namespace` as a source |
| [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Env vars, JSON/YAML/TOML/`pyproject.toml`, secrets files, cloud secret managers | CLI (when enabled) > init args > env > `.env` > defaults | pydantic model validation | Built-in CLI parsing with subcommands and help text |
| [environs](https://github.com/sloria/environs) | Env vars (Twelve-Factor focus) | Env-var oriented (single tier) | marshmallow validation + rich type casting | None |
| [python-decouple](https://github.com/HBNetwork/python-decouple) | Env vars, `.ini`/`.env` files, defaults | Env > file > default | Explicit `cast` callable; no schema validation | None |
| [Dynaconf](https://www.dynaconf.com/) | TOML/YAML/JSON/INI/Python/`.env`, env vars | Multi-environment profiles + env switcher | `Validator` objects / TOML schemas; token auto-cast | Management CLI (init/list/write/validate/export) |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | `.env` files only | None — loads into `os.environ` or a dict; caller decides layering | None (parser/loader only) | None |
| [Hydra](https://hydra.cc/docs/intro/) / [OmegaConf](https://omegaconf.readthedocs.io/) | YAML config files + command line; OmegaConf also merges dataclasses | Hierarchical composition + CLI `key=value` overrides | OmegaConf structured configs (opt-in runtime type safety) | Command-line composition is central; `@hydra.main` owns `argv` |
| [configparser](https://docs.python.org/3/library/configparser.html) (stdlib) | INI files | Multiple files read sequentially; later overrides earlier | None — values are strings; caller converts | None |

Framework and secret-manager integrations differ too: pydantic-settings
integrates with GCP/AWS/Azure secret managers; environs ships Flask and
Django helpers; Dynaconf natively replaces Django/Flask settings and
supports Vault/Redis backends. BatConf documents no framework
integrations — by scope, not omission.

## Configuration access interfaces

How each tool exposes values to application code:

| Tool | Attribute dot-path | Subscript | Notes |
|---|---|---|---|
| **BatConf** | yes | yes | dual interface; subscript supports dynamic keys |
| pydantic-settings | yes | no | typed model fields; no documented `__getitem__` |
| environs | no | no | imperative typed reads, `env.str("KEY")` |
| python-decouple | no | no | `config('KEY', ...)` per value |
| Dynaconf | yes | yes | also dotted-string keys and a callable-with-cast form |
| python-dotenv | no | yes (dict) | `dotenv_values()` returns a plain dict |
| Hydra / OmegaConf | yes | yes | `DictConfig` supports both interchangeably |
| configparser | no | yes | two-level `config['section']['key']`, string values |

Dynaconf and Hydra/OmegaConf offer the same dual attribute+subscript
access as BatConf — Dynaconf's access surface is the richest here.
pydantic-settings offers fully typed, IDE-completable attribute access,
arguably more ergonomic for static, known keys, but with no subscript
form for dynamic lookups.

## Choosing a tool

**Choose BatConf** if you want layered, precedence-based composition of
multiple config sources with zero required dependencies, plain
stdlib-dataclass schemas, explicit (non-magical) CLI wiring, and
validation kept in your application code where it belongs to you.

**Choose pydantic-settings** if you want strongly typed, validated
configuration with generated CLI parsing and cloud secret-manager
integration — especially if your codebase already uses pydantic.

**Choose environs** if you follow the Twelve-Factor model, keep all
configuration in environment variables, and want rich type casting plus
marshmallow validation, particularly in Flask or Django apps.

**Choose python-decouple** if you want a minimal, long-established way
to separate settings from code with light casting, and you do not need
schema validation, layering, or CLI integration.

**Choose Dynaconf** if you need breadth: many file formats,
multi-environment profiles, secret backends, framework replacement, and
a management CLI in a single package.

**Choose python-dotenv** if you only need to load `.env` files, as a
building block beneath your own code or another config tool.

**Choose Hydra (with OmegaConf)** if you run ML experiments or research
applications and want to compose hierarchical configs from files and
override any value from the command line per run. OmegaConf on its own
offers the YAML/dataclass merging without Hydra's experiment-runner
machinery.

**Choose configparser** if you want a zero-dependency stdlib baseline:
an INI file, string values, and typing handled by your own code.

## A note on project size

The mainstream tools above are downloaded millions of times per month
and have large communities; BatConf is a much smaller project. It is
actively maintained, a 1.0 release is on the roadmap, and professional
support is available through the
[Tidelift subscription](https://tidelift.com/subscription/pkg/pypi-batconf).
If ecosystem size and abundance of third-party examples are decisive
for your team, weigh that honestly — the mainstream tools win on that
axis today.
