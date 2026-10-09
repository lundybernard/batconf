# PR crafting

The commits of a PR land in `main` in their entirety and stay there. The
branch history is permanent, not a record kept only for the review.

Rules for the commit history of a pull request, from the base commit to the
merge. Each rule is one a reviewer can check against the branch.

Other files own the neighbouring rules:

- Test commands and the counts a PR reports: `AGENTS.md`, "Running tests".
- The `Assisted-by` trailer: `AGENTS.md`, "Commit attribution".
- Red commits in the test-first cycle: [TDD workflow](tdd.md), "Red commits".

## Scope

A PR carries one change scope. A branch that needs several scopes splits into
one PR per scope.

## Baseline

Run the gates on the base commit before the first change commit. A failure
that predates the branch lands as its own leading commit, one concern per
commit, before any change commit. With a green baseline, every later failure
belongs to a commit on the branch.

## Commit order: mechanical first

Mechanical commits precede the behaviour changes that depend on them:

- Reformat in its own commit, before any commit that edits the same files.
- Refactor in its own commit with no behaviour change, before the commit that
  changes the code inside. The reviewer reads "moved, unchanged", then
  "changed".
- Apply a lint rule in one commit, and enforce it in the gate in the next.
  When a commit introduces the gate command itself, write the command in its
  final form there.
- A linter-driven commit uses the type `lint:`.

## No churn

A hunk lands once, in its final form. A later commit of the same PR never
reverts, rewrites, or moves lines that an earlier commit of the PR added.

- A fix folds into the commit that introduced or last reworded the lines,
  which `git blame` names. The method is a `fixup!` commit and an autosquash
  rebase.
- Write each commit in its final shape. When a later commit would restructure
  it, build that structure up front, so the later commit only adds to it.
- Forced sequences are the only exceptions: a reformat that must precede the
  edits, or a lockfile that re-solves when the manifest changes.
- An edit to content that predates the PR is an ordinary commit, not a fixup.

## Bisectable history

Every commit passes the gates, not only the tip. The one exception is a red
commit of a TDD cycle: its new tests fail by design. "Red commits" in
[TDD workflow](tdd.md) states when one lands and the conditions it meets.

A commit that strengthens a gate (adds a check, enables a rule) carries the
fixes the gate now demands, or lands after them. When you rebuild a sequence,
run the fast gates at each commit and the full gates at the tip.

## Answering a review

Reviewed commits stay as reviewed, so the reviewer reads only the new delta:

- Land each accepted change at the tip as `[REVIEW FIX] <type>: <Summary>`.
- Make one commit per category of change: one style correction applied
  everywhere, or one fact correction.
- Push fast-forward, except for a rebase onto the base, which "Rebasing"
  covers. A rebase moves the reviewed commits to a new base, and every change
  that answers the review still lands as a `[REVIEW FIX]` commit.

## Rebasing

A rebase onto the base runs locally, as `git rebase -S <base>`, and pushes
with a lease. `main` requires signed commits. GitHub's "Update branch" button
and its fork sync add merge commits or unsigned commits, so every rebase onto
the base is local and signed.

When to rebase depends on the phase:

- **Before approval.** Rebase at any time, before or during review. The
  `[REVIEW FIX]` commits stay separate commits through a rebase, so the
  reviewer still reads the delta since the last review.
- **After approval.** Fold first, then catch up, as "Merge preparation"
  states.

A conflict resolution belongs to the rebased commit that conflicts. It is not
a `[REVIEW FIX]` commit, and it leaves no commit of its own in the branch
history.

## Merge preparation

After approval, the branch goes through two separate steps and one push:

1. **Fold.** Each `[REVIEW FIX]` commit folds into the commits it corrects,
   split by target into `fixup!` commits and autosquashed. The tree is then
   identical to the review tip: `git diff <review-tip> HEAD` is empty. The
   fold leaves each red commit separate from the commit that makes it pass.
2. **Catch up.** Rebase onto the current base. The required checks need the
   branch to contain the tip of the base before the merge, so this step
   always runs. It comes after the fold, because the empty-diff proof holds
   only while the fold and the catch-up stay separate.
3. **Push once**, with `--force-with-lease` pinned to the branch hash on the
   remote just before the push.

The rewritten branch meets these checks:

- A backup branch holds the review tip until the push succeeds.
- Each commit keeps its original message and trailers.
- No subject starts with `[REVIEW FIX]` or `fixup!`.
- Every commit is signed, with your own identity as committer.

## PR body

The body is a table of contents for the commits:

- One bullet per logical change.
- One verification line: the gates run, their results, and the counts
  `AGENTS.md` asks for.
- Reviewer notes, a few short bullets.

The commits and the diff carry the detail.
