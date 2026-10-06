"""Errors raised by batconf.

Every error keeps the standard exception it replaces as a base, so an
except clause written before this hierarchy existed still catches.
"""


class BatconfError(Exception):
    """Base class for every error batconf raises."""


class ConfigFileNotFound(BatconfError, FileNotFoundError):
    """A config file named by a source does not exist."""


class ConfigEnvironmentNotFound(BatconfError, ValueError):
    """A config file holds no section for the active environment."""


class InvalidFileFormat(BatconfError, ValueError):
    """A file source received a file_format it does not support."""


class ConfigValueNotFound(BatconfError, AttributeError):
    """No source and no schema default supply a required value."""


class SourceDependencyNotFound(BatconfError, ImportError):
    """An optional package a source depends on is not installed."""


__all__ = [
    'BatconfError',
    'ConfigEnvironmentNotFound',
    'ConfigFileNotFound',
    'ConfigValueNotFound',
    'InvalidFileFormat',
    'SourceDependencyNotFound',
]
