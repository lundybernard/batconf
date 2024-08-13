```{currentmodule} batconf
```
```{toctree}
:caption: Dev Guide
:hidden: true
:maxdepth: 2

```
# Developers Guide
Information to assist developers working to maintain and improve BatConf

## Install dev dependencies
`pip install --editable .[dev]`

## Install documentation dependencies
`pip install --editable .[docs]`


## Build the documentation:
```bash
> make docs
```


## Release Procedure
* Create a new release branch
  * Update your main branch, `git checkout main & git pull`
  * Checkout a release branch `git checkout -b release/vX.Y.Z`
* Update the version in {gh-file}`pyproject.toml <pyproject.toml>`
  * In most cases just remove the `+dev` suffix `0.1.2+dev -> 0.1.2`
* Add release notes to the {gh-file}`changelog <docs/source/changelog.rst>`
* Rebuild the documentation locally `make docs`, 
  and review the new changelog entry
* Commit the changes
  * `git add pyproject.toml docs/source/changelog.rst & git commit`
  * Example commit message:
    ```
    Release version X.Y.Z
    
    Fixes: #{{release ticket number}}
    ```
* Bump the version and mark it as +dev
  * Update the version in {gh-file}`pyproject.toml <pyproject.toml>`
    from `X.Y.Z` -> `X.Y.Z+dev`
  * Commit the change: `git add pyproject.toml & git commit -m 'bump version to X.Y.Z+dev'`
* Open a PR on GitHub, get it reviewed and rebase+merge these 2 commits
* Tag the release
  * update your main branch: 
    `git switch main & git pull & git fetch --all --tags`
  * Get the commit hash for the "release version..." commit, 
    not the "bump version": `git log`
  * Tag the release:
    ```
    git tag -f release {{commit#}}
    git tag -f stable & git tag stable {{commit#}}
    git tag v{{X.Y.Z}} {{commit#}}
    git push origin release stable v{{X.Y.Z}} --force
    ```
* Build and Publish to PyPi
  * Checkout release `git checkout release`
  * Build the package: `poetry build`
  * Publish to test pypi: `poetry publish -r testpypi`
  * Verify the release looks good on:
    [test.pypi](https://test.pypi.org/project/batconf/)
  * Publish to pypi: `poetry publish`
  * Verify the release on [pypi](https://pypi.org/project/batconf/)
