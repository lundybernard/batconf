import os
import warnings

from .types import SourceInterfaceP


_BAT_PREFIX_DEPRECATION = (
    "the implicit 'BAT' environment prefix is deprecated and will be "
    "removed in v0.5.0; pass prefix='BAT' to keep it, or prefix=None for "
    'no prefix.'
)


class _UnsetPrefix:
    """Sentinel type: the caller declared no prefix."""


_UNSET = _UnsetPrefix()


class EnvSource(SourceInterfaceP):
    """Configuration source that reads from environment variables.

    Keys are resolved by joining the prefix, the dotted config path and
    the key, then upper-casing the result. With ``prefix='mytool'``,
    path ``database`` and key ``host`` read ``MYTOOL_DATABASE_HOST``.

    Parameters
    ----------
    prefix : str or None, default=deprecated ``BAT``
        Environment namespace for every lookup. ``None`` declares no
        namespace. Leaving it undeclared keeps the pre-0.5.0 behaviour:
        the ``BAT`` prefix on a lookup with no path, and a
        ``DeprecationWarning``. The ``BATCONF`` namespace is reserved.

    Examples
    --------
    >>> import os
    >>> os.environ['MYTOOL_DATABASE_HOST'] = 'localhost'
    >>> src = EnvSource(prefix='mytool')
    >>> src.get(key='host', path='database')
    'localhost'
    """

    def __init__(self, prefix: str | None | _UnsetPrefix = _UNSET) -> None:
        self._prefix = prefix

    def get(self, key: str, path: str | None = None) -> str | None:
        return os.getenv(self.env_name(key, path=path))

    def env_name(self, key: str, path: str | None = None) -> str:
        """Return the environment variable name for ``key`` under ``path``."""
        parts = (
            self._prefix_parts(path)
            + (path.split('.') if path else [])
            + key.split('.')
        )
        return '_'.join(parts).upper()

    def _prefix_parts(self, path: str | None) -> list[str]:
        if not isinstance(self._prefix, _UnsetPrefix):
            return [self._prefix] if self._prefix else []
        if path:
            return []
        # stacklevel 4 reaches the caller of get():
        # get -> env_name -> _prefix_parts -> warn
        warnings.warn(
            _BAT_PREFIX_DEPRECATION,
            DeprecationWarning,
            stacklevel=4,
        )
        return ['BAT']

    def __str__(self):
        return f'Environment Variables: {repr(self)}'

    def __repr__(self):
        return f'{self.__class__.__name__}()'
