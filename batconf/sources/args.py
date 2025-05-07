from argparse import Namespace

from ..source import SourceInterface, OpStr


class CliArgsConfig(SourceInterface):
    """Legacy argparse.Namespace configuration source.

    Using this source, the key value will overwrite every
    option where the final key in its path matches.
    project.key1, project.thing1.key1, project.thing2.key1, etc.
    would all be set to "crash".

    ex:
    ```
    > bat print_config key1=crash key2=override`
    project <class 'project.cfg.ProjectConfig'>:
        |- submodule <class 'project.submodule.SubmoduleConfig'>:
        |    |- sub <class 'project.submodule.sub.MyClient.Config'>:
        |    |    |- key1: "crash"
        |    |    |- key2: "override"
        |- clients <class 'project.cfg.ClientsSchema'>:
        |    |- key1: "crash"
    ```

    This is often sufficient for smaller projects, where the name collisions
    do not cause a problem,
    and allows for simpler argparser setup where you do not need to specify
    a 'dest=' parameter for arguments.
    """

    def __init__(self, args: Namespace) -> None:
        self._data = args

    def get(self, key: str, module: OpStr = None) -> OpStr:
        key = key.split('.')[-1]

        return getattr(self._data, key, None)
