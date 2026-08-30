from batconf.sources.types import SourceInterfaceP

from argparse import Namespace


class NamespaceSource(SourceInterfaceP):
    """A configuration source
    that retrieves values from an argparse.Namespace object.

    A lookup joins ``path`` and ``key`` with a ``.`` and reads that exact
    attribute. Give each argument a ``dest`` holding its full dotted
    config path: there is no bare-key fallback, and a nested namespace is
    never walked.

    Parameters
    ----------
    namespace : argparse.Namespace
        An argparse.Namespace instance.

    Examples
    --------
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--host', dest='root.host', default='localhost')
    >>> args = parser.parse_args()
    >>> src = NamespaceSource(args)
    >>> src.get('root.host')
    'localhost'
    >>> src.get('host', path='root')
    'localhost'
    """

    def __init__(self, namespace: Namespace) -> None:
        self._data = namespace

    def get(self, key: str, path: str | None = None) -> str | None:
        attr = '.'.join((path, key)) if path else key
        return getattr(self._data, attr, None)

    def __str__(self):
        return f'Namespace Source: {repr(self)}'

    def __repr__(self):
        return f'{self.__class__.__name__}(namespace={self._data})'
