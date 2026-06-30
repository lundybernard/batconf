# batconf — agent & contributor guide

Orientation for AI coding agents (and humans) working on `batconf`. This file
is tool-agnostic. Claude Code users also receive it via `CLAUDE.md`; users of
other agents can point their tool at this file directly.

## Conventions (read when relevant)

This project follows a strict test-driven workflow and a specific Python style.
The detailed guides are vendored under `docs/agents/` and are **lazy** — read
the one that applies to the change you are making, rather than loading them all
up front:

- **[TDD workflow](docs/agents/tdd.md)** — read before writing or changing
  tested code. Outside-in, test-first, one requirement per cycle.
- **[Python style](docs/agents/python-style.md)** — read when editing `.py`
  files: test idioms, project layout, typing, and formatting.
- **[Architecture Decision Records](docs/agents/adr.md)** — read before
  proposing changes to core behaviour, or when recording a new decision.

## Source interface

`SourceInterfaceP` (Protocol, `batconf/sources/types.py`) is the canonical
source interface — prefer it for all new code. `SourceInterface` (ABC) exists
only as a temporary workaround for mypy limitations and may be removed in a
future release.

## Running tests

- Full matrix (parallel, minimal output): `nox -s parallel -- -q`
  Avoid raw `nox -p` — it interleaves all sessions and is very noisy.
- Targeted runs during development: `python -m pytest <paths>`.
