from typing import Any

import subprocess

from gurun import Node
from gurun.node import WrapperNode


class Subprocess(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(subprocess.run, *args, **kwargs)


class Workspace(Subprocess):
    def __init__(self, workspace: str, os: str, *args: Any, **kwargs: Any):
        if os.lower() == "linux":
            super().__init__("wmctrl", "-s", workspace, *args, **kwargs)
        else:
            raise ValueError("Workspace is only available on Linux")
