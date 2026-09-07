# ADR 0021 — What a format and the process environment can express

Date: 2026-09-01
Status: Proposed

## Context

Several projects share one config file and one process environment, and the
user moves between environments. The behaviour described below is the
behaviour of the sources as they ship in 0.4.1.

The `flat` and `sections` formats accept `config_env` and discard it. The
file source does not raise an error. Only `environments` holds several
environments in one file. A `flat` file has one key space, so two projects
cannot both declare `host`. Environment variables have no environment layer
at all: a variable exported while working in dev keeps overriding the file in
stage and in test until the user unsets it.

Once [an absent path is the root](0017-absent-path-mounts-at-root.md), the
root of a file and the root of the process environment belong to no
project. Today the module name separates two projects implicitly. After the
change, sharing is explicit, and batconf must state the rules for it.

## Decision

The batconf configuration environment exists only where the medium
expresses it. batconf documents the contract and adds no layer.

- `flat` and `sections` carry no configuration environment and ignore
  `config_env`. Only `environments` holds several configuration
  environments in one file.
- `sections` holds several projects in one file, for one configuration
  environment.
- Shell environment variables carry no configuration environment. The
  shell that starts the process supplies one set of values, and that set
  is the whole of it.
- In a shared file, or in a shared set of shell environment variables,
  every project declares its own name — its `path`, and its `EnvSource`
  prefix — for every source it builds. The file root and the unprefixed
  shell-variable namespace belong to no one.

## Options considered

### Document the contract; each format keeps what it expresses (chosen)

- Each format states what it can hold, so a user picks the format from the
  requirement [pro]
- A caller that builds several sources and passes one `config_env` to all
  of them stays legal [pro]
- No source gains a dimension its medium does not have [pro]
- An ignored `config_env` is still silent, so the guide has to teach
  it [con]

### Raise when a format cannot use `config_env`

- A misunderstanding surfaces at construction instead of at the first
  wrong value [pro]
- Makes one uniform `config_env` illegal across a mixed source list, which
  is a legitimate configuration [con]
- Changes documented behaviour, so it needs the same pre-freeze window as
  the rest of this group and adds no capability [con]

### Give every source an environment layer

- One rule everywhere, and a `sections` file could then hold
  environments [pro]
- The process environment holds one environment because it is one; a second
  layer inside it invents state the medium does not have [con]
- Two sources could then disagree about the active environment, and nothing
  decides between them [con]

## Rationale

A file describes three environments at once because a file is data. A
process environment cannot, because it is the environment the process runs
in. The contract follows that difference instead of papering over it, and
each format keeps the capability it actually has.

The root is an ownership claim. A project that leaves its name unset claims
the shared root, and every other project that does the same reads the same
values, with no error. The library cannot detect this: it cannot know that
a file is shared. So the rule is a documented discipline rather than a
check.

Declaring the name is cheap because one declaration covers the files.
`path=` reaches every source through the frozen `get(key, path)` parameter,
so a project names itself once on `Configuration`. The project states only
the environment prefix separately. Matching the environment namespace to the
file namespace is the recommendation and the canonical setup. `prefix=`
exists for a package rename whose deployments still export the old prefix,
and for several packages that share one prefix in one deployment. See
[the environment prefix](0018-env-source-prefix.md).

## Consequences

- A user who moves between environments needs the `environments` format, or
  one file per environment.
- `flat` is single-tenant. A shared file cannot use it.
- Every project reading a shared file must agree on one `file_format`. An
  `environments` file read as `sections` returns nothing.
- One file holds one `default_env`, and the file owns it. A project that
  wants a different environment passes `config_env=`. See
  [environment selection](0020-environment-selection-bootstrap.md).
- An exported variable outlives every edit to the file and keeps overriding
  until the user unsets it. This is the sharpest hazard in the shared case,
  and the guide must state it.
- In INI, `[DEFAULT]` keys inherit into every declared section, so one
  project can leak a key into every other project's sections.
