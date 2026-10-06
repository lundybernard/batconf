import os

from .types import SourceInterfaceP


class EnvSource(SourceInterfaceP):
    """Configuration source that reads from environment variables.

    Keys are resolved by joining the prefix, the dotted config path and
    the key, then upper-casing the result. With ``prefix='mytool'``,
    path ``database`` and key ``host`` read ``MYTOOL_DATABASE_HOST``.

    Parameters
    ----------
    prefix : str or None, default=None
        Environment namespace for every lookup. Declare one: without a
        prefix a root-level key would resolve to a bare name such as
        ``PATH`` or ``USER``. The ``BATCONF`` namespace is reserved for
        BatConf's own variables.
    raw : bool, default=False
        Read bare names at the root. Schema-declared fields then resolve
        against ambient process variables, and the collision is the
        caller's chosen trade.

    Examples
    --------
    >>> import os
    >>> os.environ['MYTOOL_DATABASE_HOST'] = 'localhost'
    >>> src = EnvSource(prefix='mytool')
    >>> src.get(key='host', path='database')
    'localhost'
    """

    def __init__(self, prefix: str | None = None, raw: bool = False) -> None:
        self._prefix = prefix
        self._raw = raw

    def get(self, key: str, path: str | None = None) -> str | None:
        if not (path or self._resolves_bare_names):
            return None
        return os.getenv(self.env_name(key, path=path))

    @property
    def _resolves_bare_names(self) -> bool:
        """A bare name is read under a prefix, or by explicit opt-in."""
        return bool(self._prefix) or self._raw

    def env_name(self, key: str, path: str | None = None) -> str:
        """Return the environment variable name for ``key`` under ``path``."""
        parts = (
            ([self._prefix] if self._prefix else [])
            + (path.split('.') if path else [])
            + key.split('.')
        )
        return '_'.join(parts).upper()

    def __str__(self):
        return f'Environment Variables: {repr(self)}'

    def __repr__(self):
        return f'{self.__class__.__name__}()'
