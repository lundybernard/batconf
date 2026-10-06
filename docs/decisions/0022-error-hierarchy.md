# ADR 0022 — A batconf error hierarchy

Date: 2026-08-30
Status: Accepted

## Context

batconf raised only standard exceptions. A missing environment section
raised `ValueError`, a required value with no default raised
`AttributeError`, a missing file raised `FileNotFoundError`, and an
absent optional dependency raised `ImportError`. None of them named
batconf.

Two costs follow.

A caller cannot tell a batconf failure from its own. Configuration is
read at start-up, inside application code that raises the same standard
types for its own reasons, so `except ValueError` around a start-up
block catches both and can report neither accurately.

The failures also arrive late. Every file source loads through a
`cached_property`, so `missing_file_option='error'` reports a bad path
at the first key access rather than at construction. A program given a
wrong config path starts normally and fails somewhere later, by which
point nothing connects the failure to the path that caused it.

Both are cheap to change now and expensive after the 1.0 freeze: the
exception types a library raises are part of its public contract.

## Decision

`BatconfError` is the base class of every error batconf raises. Each
concrete error also inherits the standard exception it replaces, so
`except ValueError` and `except FileNotFoundError` clauses written
against earlier versions keep catching. The errors are exported from
the root namespace.

Every file source checks its path while it constructs. When
`missing_file_option='error'` and the file is absent, construction
raises `ConfigFileNotFound`. The other options are unchanged: they
still report at load time, when the source knows whether it has data.

## Options considered

### A hierarchy whose members keep their stdlib bases (chosen)

- A caller can catch every batconf failure with one clause [pro]
- Existing except clauses keep working, so 1.0 needs no migration [pro]
- Each error names the failure, so a caller can act on the kind [pro]
- Every error carries two bases, which reads as unusual until the
  compatibility reason is known [con]

### Keep the standard exceptions (status quo)

- Nothing to learn and nothing to migrate [pro]
- Callers stay unable to separate batconf failures from their own [con]
- Freezes the ambiguity into the 1.0 contract, where the only remedy
  left is a major release [con]

### A clean-break hierarchy with no stdlib bases

- The class tree states one thing and is simple to read [pro]
- Every existing `except ValueError` and `except FileNotFoundError`
  around batconf stops catching [con]
- Turns a polish release into a breaking one [con]

## Rationale

The dual bases are a deliberate compromise, not an accident of design.
A clean hierarchy is the better shape in isolation; it is the wrong
shape for a release whose purpose is to freeze the API without
breaking anyone. Keeping the old base means the change is additive:
callers who want the new precision opt in by catching `BatconfError`,
and callers who do nothing keep working. Post-1.0 the dual bases are
also what allows the hierarchy to grow — a new error type slots under
`BatconfError` without any caller changing a clause.

Timing follows the same logic. Exception types are frozen at 1.0, so a
type that does not exist by then cannot appear later without a major
release. That makes this the last release in which the hierarchy can
be introduced additively.

The eager file check belongs with the hierarchy rather than after it.
`ConfigFileNotFound` exists to tell a caller which path failed, and
the lazy raise destroyed exactly that context by deferring the report
until the stack no longer showed the source. Checking at construction
is what makes the new type worth catching. The check is confined to
the `'error'` option, so the lazy design that `'warn'` and `'ignore'`
depend on is untouched.

## Consequences

- `except BatconfError` catches every failure batconf raises. Callers
  wanting one kind catch the specific class.
- The eager check is a behaviour change: a source built with
  `missing_file_option='error'` and a missing file now fails at
  construction. Code that built such a source expecting to fail later
  fails earlier instead.
- The error types are public API from 1.0. Adding a class under
  `BatconfError` stays additive; removing one, renaming one, or
  dropping a stdlib base is breaking.
- New raise sites use a batconf type. A bare standard exception raised
  from library code is now a defect.
