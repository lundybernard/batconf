"""
Internal backwards-compatibility helpers.

This module provides reusable machinery for deprecating old names within
the batconf.sources package. It is not part of the public API.
"""
import warnings


def deprecated_module(
    path: str | None, module: str | None, method: str = 'get'
) -> str | None:
    """Map the deprecated ``module`` keyword of a method onto ``path``.

    The ``module`` keyword argument is deprecated in v0.4.0 and removed in
    v0.5.0; ``path`` is its replacement. When ``module`` is supplied a
    ``DeprecationWarning`` is emitted and its value is used only if ``path``
    was not also given. ``method`` names the deprecating method, which must
    call this function directly: the warning points two frames up.
    """
    if module is not None:
        warnings.warn(
            f"the 'module' keyword argument to .{method}() is deprecated "
            "and will be removed in v0.5.0; use 'path' instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        if path is None:
            path = module
    return path
