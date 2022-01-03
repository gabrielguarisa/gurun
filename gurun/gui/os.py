from typing import Any

import subprocess

from gurun.node import WrapperNode


class Subprocess(WrapperNode):
    def __init__(self, *popenargs: Any, **kwargs: Any):
        super().__init__(subprocess.run, **kwargs)
        self._args_memory = popenargs


class Workspace(Subprocess):
    def __init__(self, workspace: str, os: str, **kwargs: Any):
        if os.lower() == "linux":
            super().__init__("wmctrl", "-s", workspace, **kwargs)
        else:
            raise ValueError("Workspace is only available on Linux")
