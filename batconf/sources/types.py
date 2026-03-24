from typing import Literal

ConfigFileFormats = Literal['flat', 'sections', 'environments']
MissingFileOption = Literal['ignore', 'warn', 'error']

__all__ = [
    'ConfigFileFormats',
    'MissingFileOption',
]
