from dataclasses import dataclass

from .sub import MyClient


@dataclass
class SubmoduleConfig:
    """Add a Config dataclass to the submodule's __init__.py

    These module-level configs act as stand-alone config trees,
    batconf.manager.Configuration builds additional lookup functions on top
    of this structure.
    """

    sub: MyClient.Config
