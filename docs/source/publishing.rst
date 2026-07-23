.. currentmodule:: batconf

Release Procedure
=================

Prerequisites: signing keys
---------------------------

Each maintainer sets up their own GPG signing key before their first release.
See :doc:`signing` for the one-time key generation, backup, and publishing
steps.

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

  * Tag the release. The version tag is GPG-signed (``-s``):

    .. code-block:: bash

       git tag -f release {{commit#}}
       git tag -f stable {{commit#}}
       git tag -s v{{X.Y.Z}} {{commit#}} -m "Release vX.Y.Z"
       # force-push only the moving tags; push the signed version tag
       # without --force so a published, immutable tag is never clobbered
       git push origin release stable --force
       git push origin v{{X.Y.Z}}

  * Verify the signature: ``git tag -v v{{X.Y.Z}}``

* Build and Publish to PyPi

  * Checkout release ``git checkout release``
  * Build the package: ``hatch build``
  * Check the artifacts: ``twine check dist/*``
  * Sign the artifacts (detached, armored):
    ``gpg --detach-sign --armor dist/*``

    * Produces a ``.asc`` signature next to each sdist/wheel.
    * PyPI no longer accepts signature uploads, so these are published
      on the GitHub Release (below), not via twine.

  * Publish to test pypi:
    ``twine upload --verbose --repository testpypi dist/*.tar.gz dist/*.whl``
  * Verify the release looks good on
    `test.pypi <https://test.pypi.org/project/batconf/>`_
  * Publish to pypi:
    ``twine upload --verbose --repository pypi dist/*.tar.gz dist/*.whl``
  * Verify the release on `pypi <https://pypi.org/project/batconf/>`_

* Create the GitHub Release

  * Draft a release for the ``v{{X.Y.Z}}`` tag at
    `github releases <https://github.com/lundybernard/batconf/releases>`_
  * Upload the build artifacts (``dist/*.tar.gz``, ``dist/*.whl``) and their
    ``.asc`` signatures so users can verify downloads against the signing key.
