# BatConf Documentation

## How to build the docs
### Install required packages
From the repository root, in an activated virtual environment:

```bash
python -m pip install --editable . --group docs
```

`--group` requires pip 25.1 or newer. Install Graphviz separately and make sure
its `dot` executable is on your PATH.


### build the document files
```bash
cd docs/
make docs
```

### Build with pixi

```bash
pixi run docs
```

pixi installs the documentation dependencies and Graphviz, then writes the HTML
to `docs/build/html`.
