# BatConf Documentation

## How to build the docs

The documentation dependencies are a
[PEP 735](https://peps.python.org/pep-0735/) dependency group named
`docs`, declared in `pyproject.toml`. They are not an optional extra,
so `.[docs]` does not resolve.

### With pixi

`pyproject.toml` defines a `docs` environment and a `docs` task, so one
command installs the group and builds:

```bash
pixi run -e docs docs
```

### With another tool

Install the group, then build:

```bash
uv sync --group docs             # uv
pip install --group docs -e .    # pip 25.1 or newer
```

```bash
cd docs/
make docs
```

`make docs` cleans, regenerates the API reference with `sphinx-apidoc`,
and writes HTML to `docs/build/html`.
