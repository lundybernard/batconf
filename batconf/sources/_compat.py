"""
Internal backwards-compatibility helpers.

This module provides reusable machinery for deprecating old names within
the batconf.sources package. It is not part of the public API.
"""
import warnings


def deprecated_module(path: str | None, module: str | None) -> str | None:
    """Map the deprecated ``module`` keyword of ``.get()`` onto ``path``.

    The ``module`` keyword argument is deprecated in v0.4.0 and removed in
    v0.5.0; ``path`` is its replacement. When ``module`` is supplied a
    ``DeprecationWarning`` is emitted and its value is used only if ``path``
    was not also given.
    """
    if module is not None:
        warnings.warn(
            "the 'module' keyword argument to .get() is deprecated and will "
            "be removed in v0.5.0; use 'path' instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        if path is None:
            path = module
    return path


def make_deprecated_getattr(
    deprecated: dict[str, str],
    module_globals: dict,
    module_name: str,
    targets: dict[str, str] | None = None,
):
    """Return a module-level ``__getattr__`` that warns on deprecated names.

    Parameters
    ----------
    deprecated : dict[str, str]
        Mapping of old name to display name used in the warning message.
    module_globals : dict
        The calling module's ``globals()`` dict, used to resolve names.
    module_name : str
        The calling module's ``__name__``, used in ``AttributeError`` messages.
    targets : dict[str, str], optional
        Overrides which globals key is returned for each old name.
        When omitted, the display name from ``deprecated`` is used as the key.

    Returns
    -------
    Callable[[str], object]
        A ``__getattr__`` function suitable for assignment at module level.
    """
    _targets = targets or {}

    def __getattr__(name: str):
        if alias := deprecated.get(name):
            warnings.warn(
                f'{name!r} is deprecated, use {alias!r} instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            return module_globals[_targets.get(name, alias)]
        raise AttributeError(
            f'module {module_name!r} has no attribute {name!r}'
        )

    return __getattr__
