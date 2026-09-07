# Architecture Decision Records (ADRs)

Significant decisions live in `docs/decisions/`. Read the relevant ADRs before
proposing changes to core behaviour, and record new significant decisions as
ADRs.

## Layout

- `docs/decisions/README.md` — index of every decision and group.
- `docs/decisions/0000-foundational/` — pre-ADR decisions, reconstructed after
  the fact. Explains the core philosophy and why the library is shaped the way
  it is. **Read this first** to understand the design.
- `docs/decisions/NNNN-title.md` — a standalone decision.
- `docs/decisions/NNNN-topic/` — a group of decisions made for one feature or
  migration. The directory number names the umbrella decision, and the member
  ADRs take the numbers that follow. Each group has a `README.md` index and
  often a `REQUIREMENTS.md`.

## When to read

Before changing core behaviour — source resolution, the source interface, the
config schema, deprecation cycles — read the foundational ADRs and any group
touching that area.

## Writing a new ADR

When the decisions directory already exists, just write the new file — do not
reconstruct the whole structure. Read one or two existing ADRs first to match
conventions.

### Naming

One global four-digit sequence covers the whole tree. Standalone ADRs, group
directories, and group members draw from it, and no number repeats. Take the
next free numbers from the index in `docs/decisions/README.md`.

- **Standalone decision:** `docs/decisions/NNNN-title.md`.
- **Group directory:** `docs/decisions/NNNN-topic/`. The directory number
  names the umbrella decision, and its members continue the sequence: a
  `0020-topic/` group of three decisions numbers them `0021`–`0023`.
- **Support files** — `README.md`, `REQUIREMENTS.md`, `PLAN.md`, `DESIGN.md` —
  carry no number.
- Four-digit prefix + descriptive kebab-case name (`0021-root-section.md`).
- Cite another ADR as `ADR NNNN` with a relative link:
  `[ADR 0019](0016-root-path-and-namespaces/0019-ini-root-section.md)`.

A number on an unmerged branch is a placeholder. The number is final when the
ADR merges to the main branch, because another branch may claim it first. On a
rebase, take the next free numbers on the base branch and update every
reference to them.

### File format

```markdown
# ADR NNNN — Title

Date: YYYY-MM-DD
Status: Proposed | Accepted | Deprecated | Superseded by NNNN

## Context
<What problem required a decision. What constraints existed.>

## Decision
<What was decided. Be specific — name the class, method, or convention.
Present tense: describe what the change implements.>

## Options considered

### Option name (chosen)

- reason it helps [pro]
- reason it costs [con]

### Other option

- reason [pro]
- reason [con]

## Rationale
<Why the chosen option over the others. Include philosophy, not just
mechanics. If the decision was pragmatic or a workaround, say so explicitly.>

## Consequences
<What became easier or harder. What future decisions this constrains.
What callers or contributors must know.>
```

### Options format — the one hard rule

Each option is a named subsection (`### Option name`) with `[pro]` / `[con]`
bullets. **Never** use a `| Option | Pros | Cons |` table. Mark the chosen
option with `(chosen)` in its heading.

### Status convention

- `Proposed` while the PR is open; `Accepted` after merge.
- ADRs are immutable once accepted. To reverse one, write a **new** ADR with
  `Status: Superseded by NNNN` (and set the old one to `Superseded`).
- Statuses: `Proposed → Accepted → Deprecated / Superseded by NNNN`.

### Update the index

Add a row to `docs/decisions/README.md`. A group row links the directory and
names its member range: `Root path and namespaces (components 0017–0021)`. Add
a new member ADR to the group's own `README.md` as well.
