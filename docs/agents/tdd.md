# TDD workflow

The test-driven-development workflow for this project. Language- and
framework-agnostic in principle; the concrete runner, layout, and idioms come
from [Python style](python-style.md). This guide owns the *process*.

Based on the GOOS (Freeman & Pryce) double-loop, generalized to one loop per
test layer (see N-loop below).

---

## Core

Outside-in TDD. No implementation without a failing test. Red for the right
reason before green. One requirement per cycle — never bundle.

**YAGNI** (scope): build only what a failing test demands. Defer every
speculative abstraction, collaborator, or config until a requirement forces it.
Distinct from naive-first: YAGNI governs *what you don't add*; naive-first (the
implement step) governs *how simply you green what you do add*.

---

## Test layers

Ordered outermost to innermost; each is a gate (a stage runs only if the
earlier stage is fully green):

- **e2e** — the deployed system end to end.
- **behavioral** — black-box round-trip / scenario tests; the public API used as
  a consumer would, doubling as worked-example documentation.
- **integration** — per-module contract against real dependencies (stub only
  true external services). One test per public attribute/method, subtests per
  code-path. State verification.
- **unit** — isolation tests; collaborators mocked. Behavior/interaction
  verification.

Concrete directories, runner, and mocking tools come from
[Python style](python-style.md).

---

## N-loop: descend, implement, refactor, ascend

The double loop generalized to one loop per layer. The loop count is flexible —
skip layers a given change does not touch.

1. **Add** the new top-level test(s) at the highest appropriate layer (the outer
   red).
2. **Descend**: pick a **single** failing test. Write the **minimal** tests one
   layer down needed to resolve *just that one failure*. Recurse downward until
   the unit tests required exist, all failing for the right reason.
3. **Implement** the naive solution to green the unit tests.
4. **Refactor** — now that it is green, take the opportunity. Tests must stay
   green through the refactor.
5. **Ascend** the layers until one more failing test appears. Repeat from 2.

Each layer gets its own red → green → refactor cycle.

---

## Staged loop (per requirement, naive-first)

Within a descent, drive one requirement at a time, ratcheting constraints down:

1. **Integration test first, from the consumer's POV** — call the public API as
   a user would. The test is a design tool: get the API shape and ergonomics
   right *before* writing anything beneath it. Adjust until the call site reads
   well.
2. **Minimal unit test, naive** — the simplest thing that could work: in-memory,
   no infra, no collaborators.
3. **Implement to green** — naive implementation satisfying steps 1 + 2.
4. **Add the next requirement to the unit test** (e.g. "must persist via the
   event store"). The new expectation fails and *cascades down*: it drives the
   new collaborator's own integration test + implementation. Recurse from step 1
   for that collaborator.

Naive-first, then tighten constraints through the unit test — each new
constraint surfaces the next component to build.

---

## Refactor discipline

- Refactor only when green.
- **Tests adapt to the code, never code to tests.** Never add dependency
  injection, seams, or factory params *solely* to ease testing. Add them only
  when production has an independent reason. "I couldn't test it otherwise" is
  not justification — prefer mocking the impl detail or a black-box round-trip.
- Designs that make tests simpler are worth choosing, but need a justification
  beyond testability.

---

## London vs Detroit

Two schools; this project uses a deliberate **hybrid**:

- **London (mockist, outside-in)** — mock collaborators, verify *calls*. Drives
  design top-down (the test discovers the next collaborator). Used at the **unit**
  layer. Cost: tests know the collaboration structure → more refactor-brittle.
- **Detroit (classic / Chicago)** — real objects, mock only true external
  boundaries, verify *state / return values*. Refactor-friendly; design feedback
  arrives later. Used at the **integration** layer and below it as the bottom
  contract.

Outside-in descent across layers = London; the bottom contract = Detroit.
