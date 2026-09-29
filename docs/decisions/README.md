# Architecture Decision Records

Significant decisions made during the development of `batconf`. Each ADR
captures context, options considered, and rationale so future contributors
understand _why_ the codebase looks the way it does.

## Conventions

- **Standalone decisions** live directly here as `NNNN-title.md`.
- **Grouped changes** get a numbered subdirectory: `NNNN-topic/`.
- ADRs are immutable once accepted. To reverse a decision, write a new ADR
  with `Status: Supersedes NNNN`.

One global four-digit sequence numbers every ADR, and no number repeats. A
group directory takes its own number and names the umbrella decision; its
member ADRs take the numbers that follow. Support files — `README.md`,
`REQUIREMENTS.md`, `PLAN.md`, `DESIGN.md` — carry no number. Cite an ADR as
`ADR NNNN` with a relative link.

Statuses: `Proposed → Accepted → Deprecated / Superseded by NNNN`

## Index

| #                                            | Title                                              | Status   |
| -------------------------------------------- | -------------------------------------------------- | -------- |
| [0000](0000-foundational/)                   | Foundational decisions (components 0001–0008)      | Accepted |
| [0009](0009-file-source-classes/)            | FileSource class refactor (components 0010–0013)   | Accepted |
| [0014](0014-get-path-parameter.md)           | Standardize `.get()` on `path`; deprecate `module` | Accepted |
| [0015](0015-retire-source-interface-abc.md)  | Retire the `SourceInterface` ABC                   | Accepted |
| [0016](0016-root-path-and-namespaces/)       | Root path and namespaces (components 0017–0021)    | Proposed |
