# Architecture Decision Records

Significant decisions made during the development of `batconf`. Each ADR
captures context, options considered, and rationale so future contributors
understand _why_ the codebase looks the way it does.

## Conventions

- **Standalone decisions** live directly here as `NNNN-title.md`.
- **Grouped changes** get a numbered subdirectory: `NNNN-topic/`.
- ADRs are immutable once accepted. To reverse a decision, write a new ADR
  with `Status: Supersedes NNNN`.

Statuses: `Proposed → Accepted → Deprecated / Superseded by NNNN`

## Index

| #                                              | Title                          | Status   |
| ---------------------------------------------- | ------------------------------ | -------- |
| [0000](0000-foundational/)                     | Foundational decisions (8 decisions) | Accepted |
| [0001](0001-file-source-classes/)              | FileSource class refactor (4 decisions) | Proposed |
| [0002](0002-get-path-parameter.md)             | Standardize `.get()` on `path`; deprecate `module` | Proposed |
