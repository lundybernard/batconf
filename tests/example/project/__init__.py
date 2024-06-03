from dataclasses import dataclass

from .submodule import SubmoduleConfig


@dataclass
class ProjectConfig:
    """Create a project-level Config class, and "plug-in" the submodules

    Note the modular nature, this entire project could be plugged into
    a larger project as a submodule.
    Submodules from this project can easily be moved within the project tree
    or spun off into their own projects.
    """

    submodule: SubmoduleConfig
