.. currentmodule:: batconf

Developer's Guide
=================

Information to assist developers working to maintain and improve BatConf.

.. toctree::
   :maxdepth: 2

   setup
   publishing
   builddocs
   signing


Crafting a pull request
-----------------------

The commits of a pull request land in ``main`` in their entirety and stay
there, so the history you craft is permanent. It does not exist only for the
review. Readers of ``git log`` and ``git blame`` rely on it long after the
merge, and that permanence is why we ask for care with it. This section
describes the commit style we like. Before a pull request merges, its history
is cleaned up to match this style.

We ask you to follow the style from the start, because that makes the review
smoother. You do not have to meet it to open a pull request. The maintainers
help you throughout the process, including the final cleanup before the
merge.

Lint first
   Put a formatter or linter change in its own commit, before the commits
   that edit the same files. The reviewer then reads "reformatted" and
   "changed" as two steps, and the real change does not hide in the noise.

One concern per commit
   Each commit makes one logical change, and the pull request covers one
   scope. Each commit then makes sense on its own, and ``git bisect`` lands
   on a small change.

No churn
   Write each change once. If a later commit would rewrite lines that an
   earlier commit of the same pull request added, fold the correction into
   that earlier commit instead, so the reviewer reads the code once. The
   interactive rebase below does this.

During review, we recommend that you answer the comments with a new commit at
the tip of the branch, titled ``[REVIEW FIX] <message>``. The reviewer then
reads only what changed since the last review. Before the merge, fold each fix
into the commit it corrects with an interactive rebase. In the editor, move
the fix below that commit and change its ``pick`` to ``fixup``:

.. code-block:: bash

   git commit -m '[REVIEW FIX] <message>'
   git rebase -i main

Coding agents follow a stricter version of this style, in
:gh-file:`docs/agents/pr-crafting.md`.
