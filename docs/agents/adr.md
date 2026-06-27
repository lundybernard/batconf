# Architecture Decision Records (ADRs)

Significant decisions live in `docs/decisions/`. Read the relevant ADRs before
proposing changes to core behaviour, and record new significant decisions as
ADRs.

## Layout

- `docs/decisions/README.md` — index of every decision and group.
- `docs/decisions/0000-foundational/` — pre-ADR decisions, reconstructed after
  the fact. Explains the core philosophy and why the library is shaped the way
  it is. **Read this first** to understand the design.
- `docs/decisions/NNNN-title.md` — a standalone decision, globally numbered.
- `docs/decisions/NNNN-topic/` — a group of decisions made for one feature or
  migration. Each group has a `README.md` index and often a `REQUIREMENTS.md`.
  Files inside are numbered locally (`NN-title.md`, starting at `01`).

## When to read

Before changing core behaviour — source resolution, the source interface, the
config schema, deprecation cycles — read the foundational ADRs and any group
touching that area.

## Writing a new ADR

When the decisions directory already exists, just write the new file — do not
reconstruct the whole structure. Read one or two existing ADRs first to match
conventions.

### Naming

- **Standalone decision:** `docs/decisions/NNNN-title.md` — globally numbered.
  Continue numbering from the next available number (check the index).
- **Inside a grouped directory:** `docs/decisions/NNNN-topic/NN-title.md` —
  numbering is **local to the group**, starting at `01`. No global number in the
  filename.
- Two-/four-digit prefix + descriptive kebab-case name (`01-foo.md`,
  `0002-bar.md`).

### File format

```markdown
# Title

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

Add a row to `docs/decisions/README.md`. For a grouped directory, also ensure
the top-level index links the group, and add the new ADR to the group's own
`README.md`.
