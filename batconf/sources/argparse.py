from batconf.source import SourceInterface

from argparse import Namespace


class NamespaceConfig(SourceInterface):
    """A configuration source
    that retrieves values from an argparse.Namespace object.

    parameters
    ----------
    namespace : argparse.Namespace:
        An argparse.Namespace instance.

    Examples
    --------
    >>> parser = argparse.ArgumentParser()
    >>> parser.add_argument('--host', dest='root.host', default='localhost')
    >>> args = parser.parse_args()
    >>> config = NamespaceConfig(args)
    >>> config.get('root.host')
    'localhost'
    """

    def __init__(self, namespace: Namespace) -> None:
        self._data = namespace

    def get(self, key: str, module: str | None = None) -> str | None:
        path = '.'.join((module, key)) if module else key
        return getattr(self._data, path, None)

    def __str__(self):
        return f'Namespace Source: {repr(self)}'

    def __repr__(self):
        return f'{self.__class__.__name__}(namespace={self._data})'
