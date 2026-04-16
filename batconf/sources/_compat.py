"""
Internal backwards-compatibility helpers.

This module provides reusable machinery for deprecating old names within
the batconf.sources package. It is not part of the public API.
"""
import warnings


def make_deprecated_getattr(
    deprecated: dict[str, str],
    module_globals: dict,
    module_name: str,
):
    """Return a module-level ``__getattr__`` that warns on deprecated names.

    Parameters
    ----------
    deprecated : dict[str, str]
        Mapping of old name to new name.
    module_globals : dict
        The calling module's ``globals()`` dict, used to resolve new names.
    module_name : str
        The calling module's ``__name__``, used in ``AttributeError`` messages.

    Returns
    -------
    Callable[[str], object]
        A ``__getattr__`` function suitable for assignment at module level.
    """

    def __getattr__(name: str):
        if alias := deprecated.get(name):
            warnings.warn(
                f'{name!r} is deprecated, use {alias!r} instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            return module_globals[alias]
        raise AttributeError(
            f'module {module_name!r} has no attribute {name!r}'
        )

    return __getattr__
