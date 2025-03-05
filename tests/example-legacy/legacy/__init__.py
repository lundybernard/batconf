from dataclasses import dataclass

from .submodule import SubmoduleConfig


@dataclass
class ProjectConfig:
    """Create a legacy-level Config class, and "plug-in" the submodules

    Note the modular nature, this entire legacy could be plugged into
    a larger legacy as a submodule.
    Submodules from this legacy can easily be moved within the legacy tree
    or spun off into their own projects.
    """

    submodule: SubmoduleConfig
