# Python style

Python coding conventions for this project. Read when working on `.py` files.
The TDD *process* lives in [TDD workflow](tdd.md); this guide covers the
Python/project specifics.

---

## Testing (Python specifics)

Concrete layer mapping:
- `tests/` — integration / e2e tests against real dependencies, public API.
- `src/<pkg>/tests/` (here: `batconf/**/tests/`) — isolated unit tests,
  external deps mocked in `setUp`.

Prefer `unittest.TestCase`. Pytest-style classes are acceptable — match
existing project style.

Import-behavior tests and anything touching `sys.modules` or mocking imports
belong in integration tests, not unit tests.

Stdlib conditional imports (e.g. `tomllib`): use `try/except` with
`# type: ignore`, not `sys.version_info` gates. Put `# noqa` **before**
`# type: ignore` on the same line.

---

## Project architecture

Standard layout for apps, services, and libraries, following the project
template (`lundybernard/project_template`):

```
src/<pkg>/
  __init__.py    # __version__; root GlobalConfig dataclass when config is used
  conf.py        # get_config(...) -> batconf Configuration  (added when needed)
  lib.py         # high-level business-logic functions — the public API
  <domain>.py    # classes holding the complex logic that lib.py orchestrates
  tests/         # unit tests (collaborators mocked)
tests/           # integration / feature tests (real deps), the public contract
```

Principles:

- **`lib.py` is thin and readable** — high-level functions (`add_x`, `get_x`)
  that read clearly for junior devs and non-technical readers. The majority of
  complex logic is factored out into classes that `lib.py` calls, keeping its
  implementation high-level and obvious.
- **Functions are the public API**, not a god-class. Designed to be useful
  across every consumer: library import, scripts, CLI, TUI, GUI, web-API
  endpoints.
- **Config is an optional convenience, never required.** Functions work
  stand-alone with sensible defaults. batconf wiring (`conf.py`, a
  `Configuration` passed in) is added only when configuration is actually
  needed — and the dependency is added then, not before.
- **`conf.py` / batconf**: `get_config(...)` composes a prioritized source
  list (CLI > env > config file > dataclass defaults) into a `Configuration`.
  High-level functions that need config take it as a parameter
  (`fn(conf, ...)`); they build their collaborators from it. Use the current
  `NamespaceConfig` (`batconf.sources.argparse`), not deprecated `CliArgsConfig`.
  `GlobalConfig` must use real-class field annotations (no
  `from __future__ import annotations`) — batconf inspects live types.

---

## unittest.TestCase idioms

**Unit tests are isolation tests.** Import only the module under test (e.g.
`from pkg import lib` / `from pkg.lib import fn`). Do not import its
collaborators, sibling modules, or their types — patch them in `setUp` and
access them through the module under test. Direct imports of other source
modules belong in integration tests, not unit tests.

**No negatively-phrased / documentation tests in unit tests.** Don't assert a
value is *not* some unrelated thing (e.g. `assertNotIsInstance(x,
BaseException)` to "document" that an error type isn't an exception). These
assert intent rather than behavior. A unit test asserts what the unit *does*;
documentation-focused / behavioral checks belong in the integration suite, if
anywhere. (Asserting the real contract of an operator — e.g. `assertNotEqual`
to verify `__eq__` distinguishes two values — is behavior, and is fine.)

Use `t` instead of `self` for the test instance:

```python
def setUp(t) -> None:  # pylint: disable=arguments-renamed
def test_something(t) -> None:
```

Patch external deps in `setUp` with `addCleanup` so every test starts clean:

```python
SRC = 'mypackage.mymodule'

def setUp(t) -> None:
    for target in ('dep_one', 'dep_two'):
        patcher = patch(f'{SRC}.{target}', autospec=True)
        setattr(t, target, patcher.start())
        t.addCleanup(patcher.stop)
```

One `TestCase` per subject. Class too large = subject doing too much; split the
subject, not the test class.

**One `test_<attr>` per public attribute; every code-path (valid/invalid/edge/
branch) is a `subTest` inside it — never a second method.** No
`test_<attr>_<variant>` (`test_add_customer_invalid`): names a condition,
fragments the attribute, dodges the no-assertion-suffix rule. Name after the
thing tested, not the assertion — `test_widget` not `test_widget_returns_value`.
Open `with t.subTest('valid'):`, loop the rest; `mock.reset_mock()` atop each
later subTest that reuses a mock.

Create the subject in `setUp` using a class-initials name — `t.ab = AlphaBeta()`,
`t.xy = XrayYankie()`. Reuse across subtests; set needed state at the start of
each subTest, no fresh inline instances.

Annotate defaulted params with comments:

```python
t.subject = MyClass(
    input='valid',
    # Default: mode='strict',
    # Default: retries=3,
)
```

---

## Property state-machine pattern

Model multi-step loading/parsing as a `cached_property` chain. Each property =
one step, computes from the prior, caches its result.

```python
class ThingLoader:
    def __init__(self, raw: str) -> None:
        self._raw = raw             # eager: pure derivation, no I/O

    @cached_property
    def parsed(self) -> str | None: ...   # validates; returns value or None

    @cached_property
    def resource(self): ...               # I/O; depends on parsed

    @cached_property
    def result(self): ...                 # extracts from resource
```

Validator properties return the value when valid, `None` when not — `if
self.parsed:` not `if self.is_valid:`. Properties are objects, not questions.

`cached_property` for I/O and non-trivial computation only. Pure string/data
derivations → `__init__` plain attributes.

Test each property in isolation by setting upstream directly — `cached_property`
stores in `__dict__`, so assignment bypasses computation:

```python
def test_result(t) -> None:
    t.subject.resource = Mock(value='expected')
    t.assertEqual(t.subject.result, 'expected')
```

---

## Code style

Ruff for formatting/linting (configured in `pyproject.toml`). Single quotes.
79-char limit — a pragmatic guide, not a hard rule.

Type annotations always. `Protocol` over ABCs. Composition over inheritance.

### Comprehension formatting

Hand-formatted comprehensions. Multi-clause: one clause per line; `if`/`and`
indented under `for`:

```python
Y = [x**2 for x in X]          # single clause: one line is fine

Y = [
    x**2
    for x in X
    if x >= 0
]

matrix = [
    (key, value)
    for key in keys
        if key.startswith('a')
    for value in values
        if value >= 0
]
```

Ruff mangles this. Wrap with `# fmt: off` / `# fmt: on` — an accepted cost.

---

## Import style

Import specific symbols, not whole modules — keeps `patch` targets unambiguous.

**Exception:** never `from sys import stderr`. pytest's `capsys` replaces
`sys.stderr` at call time; a directly-imported name bypasses it. Keep
`import sys` and use `sys.stderr.write(...)`.

---

## Docstrings

SciPy/NumPy conventions (`Parameters`, `Returns`, `Raises` sections with
underline headers). For `cached_property` descriptors, a one-liner plus `Raises`
is sufficient.
