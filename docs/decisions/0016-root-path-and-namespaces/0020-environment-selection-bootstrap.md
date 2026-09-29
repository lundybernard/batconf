# ADR 0020 — Environment selection layers above the sources

Date: 2026-09-01
Status: Proposed

## Context

A file source resolves the active environment from the `config_env`
argument, and otherwise from the `default_env` key in the file.
[ADR 0005](../0000-foundational/0005-multi-environment-file-format.md)
records the environment override as something the caller reads and passes
as `config_env`.

Users want a shell-level selector: one variable that names the environment
for every tool started in that shell. Nothing in the library reads such a
variable, and no batconf-owned variable exists. The question is whether the
sources should read one.

The same question governs other pre-configuration facts. The program must
know which config file to read, and where to look for it, before it can build
the configuration that would describe them.

## Decision

Sources never read `BATCONF_ENVIRONMENT`. The variable is the canonical
shell-level environment selector, and it is permanent. It is canonical, not
enforced: a project may select its environment another way.

The blessed layering pattern is the two-stage bootstrap. A bootstrap
`Configuration` mounts at the root over `EnvSource(prefix='batconf')`, and
optionally over a bootstrap file. Every field it declares therefore lands in
the reserved namespace: `environment` reads `BATCONF_ENVIRONMENT`, and
`config_file` reads `BATCONF_CONFIG_FILE`. It carries the environment name,
the config file paths, and other pre-configuration metadata. The caller then
builds the real configuration with `config_env=` taken from the bootstrap
value.

Precedence is: an explicit `config_env=` first, `BATCONF_ENVIRONMENT` next
through the bootstrap, and the file's `default_env` last.

The file key stays `default_env`. The argument stays `config_env=`.

Reading `BATCONF_ENVIRONMENT` through the bootstrap prefix is the sanctioned
use of the reserved namespace. From 0.5.0, a bootstrap that also needs a
genuinely ambient value, such as `$HOME`, adds a second
`EnvSource(raw=True)`. In 0.4.1, `EnvSource(prefix=None)` does that job. The
two are separate sources because a prefix applies to every lookup its source
serves. See [the environment prefix](0018-env-source-prefix.md).

## Options considered

### A two-stage bootstrap, with sources left as readers (chosen)

- The caller selects the environment once, at construction, and can see that
  choice there [pro]
- The bootstrap is an ordinary `Configuration`, so the pattern does not need
  new machinery [pro]
- No source gains a semantic contract that third-party sources would have
  to honour [pro]
- The caller writes two constructions instead of one [con]

### Every source reads the variable

- The shell selects the environment with no code in the caller [pro]
- Each source must implement the same read, third-party sources included, and
  batconf cannot force any of them to [con]
- A source's answer then depends on ambient state that its arguments do not
  show [con]

### `Configuration` reads the variable and passes it down

- One implementation, and the sources stay pure [pro]
- Bakes one variable name into the manager, where a project cannot
  substitute its own [con]
- Construction depends on ambient state invisibly, so two identical calls
  differ by shell [con]

### No blessed pattern; each caller reads the variable

- The status quo, and it costs nothing [pro]
- Every project invents its own bootstrap [con]
- No canonical name exists, so tools sharing one shell disagree about which
  variable selects the environment [con]

## Rationale

Context belongs at construction time. A `*Source` class reads one
config-source (a file, the shell environment, and so on) and answers one key
lookup. The active environment is not a property of any config-source. It is
a property of the running program, so the program selects it and passes it
to each `*Source` class at construction.

Keeping the decision above the sources leaves no cross-source semantic
contract to enforce. That matters because the source interface is open:
anyone may implement `SourceInterfaceP`, and a rule that only the shipped
sources follow is not a rule.

The bootstrap does not need new machinery because it is the library reading
its own settings with its own tool. The root mount is what makes it cheap: a
bootstrap configuration mounts at the root and does not need a namespace of
its own.

The names do not change. `default_env` and `config_env=` are documented
surface, and renaming them buys nothing.

The pattern also has room to grow. A future default-configuration factory
absorbs it, so a caller gets both stages from one call. Under that factory,
operating-system config-directory defaults become field values on the
bootstrap schema, rather than search behaviour baked into every source.

## Consequences

- `BATCONF_ENVIRONMENT` is permanent and documented. It is canonical, not
  enforced.
- No source reads an environment variable to decide its own environment. A
  source that did would break the precedence order.
- The bootstrap is the only sanctioned reader of the reserved `BATCONF_*`
  namespace.
- Precedence is fixed: `config_env=`, then `BATCONF_ENVIRONMENT`, then
  `default_env`.
- A future default-configuration factory implements this pattern; it does
  not change it. Config-directory defaults belong on the bootstrap schema.
- The environment layer applies to files. Environment variables carry no
  environment. See
  [the format and environment contract](0021-format-environment-contract.md).
