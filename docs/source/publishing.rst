.. currentmodule:: batconf

Release Procedure
=================

Prerequisites: signing keys
---------------------------

Each maintainer sets up their own GPG signing key before their first release.
See :doc:`signing` for the one-time key generation, backup, and publishing
steps.

Every signing command below names your key explicitly with ``-u``. Never rely
on the gpg default key: without ``-u``, gpg signs with whichever secret key it
considers default, which may not be the key listed for you in
:gh-file:`docs/SECURITY.md <docs/SECURITY.md>` — the resulting signature then
fails verification against the project's trust anchor
(:gh-file:`KEYS <KEYS>`). Throughout, ``{{FINGERPRINT}}`` is your
primary-key fingerprint exactly as listed in your row of the
authorized-signers table in :gh-file:`docs/SECURITY.md <docs/SECURITY.md>`
(40 hex characters, no spaces — the ``$FPR`` from :doc:`signing`). Naming the
primary key is enough; gpg selects your newest signing subkey automatically.

Steps
-----

* Create a clean git workspace: ``git worktree add ../batconf-release main``

  * switch to the release directory ``cd ../batconf-release``

* Create a new release branch

  * Update your main branch, ``git checkout main && git pull``
  * Checkout a release branch ``git checkout -b release/vX.Y.Z``

* Update the version in :gh-file:`pyproject.toml <pyproject.toml>`

  * In most cases just remove the ``+dev`` suffix ``0.1.2+dev -> 0.1.2``

* Add release notes to the :gh-file:`changelog <docs/source/changelog.rst>`

  * Change the release date from TBD to the appropriate date.

* Rebuild the documentation locally ``make docs``,
  and review the new changelog entry

* Commit the changes

  * ``git add pyproject.toml docs/source/changelog.rst && git commit``
  * Example commit message:

    .. code-block::

       Release version X.Y.Z

       Fixes: #{{release ticket number}}

* Bump the version and mark it as +dev

  * Update the version in :gh-file:`pyproject.toml <pyproject.toml>`
    from ``X.Y.Z`` -> ``X.Y.Z+dev``
  * Commit the change:
    ``git add pyproject.toml && git commit -m 'bump version to X.Y.Z+dev'``

* Open a PR on GitHub, get it reviewed and merge it with a **merge commit**
  (not rebase/squash). A merge commit preserves the original, GPG-signed
  release and ``+dev`` commits verbatim; rebase/squash rewrites them and
  strips their signatures.

* Tag the release

  * Update your main branch:
    ``git switch main && git pull && git fetch --all --tags``
  * Get the commit hash for the "release version..." commit,
    not the "+dev version" and not the merge commit: ``git log``

    * Because the merge preserves SHAs, this hash matches the release
      commit on your local release branch.

  * Tag the release. The version tag is GPG-signed (``-s``) with your key
    named explicitly (``-u``):

    .. code-block:: bash

       git tag -f release {{commit#}}
       git tag -f stable {{commit#}}
       git tag -s -u {{FINGERPRINT}} v{{X.Y.Z}} {{commit#}} -m "Release vX.Y.Z"
       # force-push only the moving tags; push the signed version tag
       # without --force so a published, immutable tag is never clobbered
       git push origin release stable --force
       git push origin v{{X.Y.Z}}

  * Verify the signature: ``git tag -v v{{X.Y.Z}}``

* Build and Publish to PyPi

  * Checkout release ``git checkout release``
  * Build the package: ``hatch build``
  * Check the artifacts: ``twine check dist/*``
  * Publish to test pypi:
    ``twine upload --verbose --repository testpypi dist/*.tar.gz dist/*.whl``
  * Verify the release looks good on
    `test.pypi <https://test.pypi.org/project/batconf/>`_

  * Sign the artifacts (detached, armored), naming your key explicitly:

    .. code-block:: bash

       gpg -u {{FINGERPRINT}} --detach-sign --armor dist/batconf-X.Y.Z.tar.gz
       gpg -u {{FINGERPRINT}} --detach-sign --armor dist/batconf-X.Y.Z-py3-none-any.whl

    * Produces a ``.asc`` signature next to each sdist/wheel.
    * PyPI no longer accepts signature uploads, so these are published
      on the GitHub Release (below), not via twine.
    * Sign each filename explicitly rather than ``dist/*``: the glob also
      matches leftover ``.asc`` files on a re-sign, so gpg prompts to
      overwrite them (a missed prompt silently keeps a stale signature)
      and signs the ``.asc`` files too.

    .. warning::

       Do **not** rebuild — ``hatch build``, ``python -m build``, or any
       other build — after signing, or after the test.pypi upload. Build
       output is not byte-reproducible, so a rebuild produces new bytes:
       every ``.asc`` becomes invalid, and the files published to PyPI would
       no longer be the ones you verified. Sign and publish the *same*
       ``dist/`` files you uploaded to test.pypi. If ``dist/`` was
       regenerated anyway, re-download the canonical files from test.pypi,
       re-sign them, and re-verify.

  * Verify the signatures **before** publishing to real pypi:

    .. code-block:: bash

       gpg --verify dist/batconf-X.Y.Z.tar.gz.asc dist/batconf-X.Y.Z.tar.gz
       gpg --verify dist/batconf-X.Y.Z-py3-none-any.whl.asc \
           dist/batconf-X.Y.Z-py3-none-any.whl
       git tag -v v{{X.Y.Z}}

    * Each must report ``Good signature`` **and** a primary key fingerprint
      matching your row in :gh-file:`docs/SECURITY.md <docs/SECURITY.md>`.
      A good signature from an unexpected key is a failure, not a pass.

  * Publish the **same** files to pypi:
    ``twine upload --verbose --repository pypi dist/*.tar.gz dist/*.whl``
  * Verify the release on `pypi <https://pypi.org/project/batconf/>`_

* Create the GitHub Release

  * Draft a release for the ``v{{X.Y.Z}}`` tag at
    `github releases <https://github.com/lundybernard/batconf/releases>`_
  * Upload the build artifacts (``dist/*.tar.gz``, ``dist/*.whl``) and their
    ``.asc`` signatures so users can verify downloads against the signing key.

* Activate the new version on ReadTheDocs

  * On the ReadTheDocs dashboard (Versions), find or add the ``v{{X.Y.Z}}``
    tag and enable its **Active** toggle.
  * Confirm `stable <https://batconf.readthedocs.io/en/stable/>`_ serves the
    new release — ``stable`` tracks the highest activated version tag — and
    that `migration.html <https://batconf.readthedocs.io/en/stable/migration.html>`_
    resolves (the PyPI README links to it).
