# Root Path and Namespaces (5 decisions)

Issues: #152 (root / default config path naming), #150 (multiple top-level
schemas)

A schema mounts at the root of a namespace the caller declares.
`Configuration` does not derive a namespace from the source tree. No reserved
word enters the path vocabulary. INI alone spells the root with a reserved
section name, because the format has no unnamed section.

Five decisions build that up: what an absent path means, how the caller
names the environment namespace, how INI reaches a root it cannot spell,
where environment selection happens, and what a shared file and a shared
process environment can express. Each option below was measured against the
behaviour of the sources as they ship in 0.4.1.

| #  | Title                                                                                    | Status   |
| -- | ---------------------------------------------------------------------------------------- | -------- |
| 01 | [An absent path mounts the schema at the root](01-absent-path-mounts-at-root.md)          | Proposed |
| 02 | [A caller-declared environment-variable prefix](02-env-source-prefix.md)                  | Proposed |
| 03 | [The INI root section](03-ini-root-section.md)                                            | Proposed |
| 04 | [Environment selection layers above the sources](04-environment-selection-bootstrap.md)   | Proposed |
| 05 | [What a format and the process environment can express](05-format-environment-contract.md) | Proposed |

## Release schedule

Two deprecations land in 0.4.1 and are removed in 0.5.0: the
`path = config_class.__module__` fallback (01) and the hardcoded `BAT`
environment prefix (02). Both change documented behaviour, so both precede
the 1.0 freeze.

Decision 03 adds a capability. `[/ROOT/]` is the one INI spelling of the root.
The `flat` layout's `root` section name is internal, and no flat file
changes. Decisions 04 and 05 add capability or state a contract. Neither
removes a working behaviour.
