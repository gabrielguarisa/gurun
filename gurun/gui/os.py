from typing import Any

import subprocess

from gurun import Node


class Subprocess(Node):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(**kwargs)
        self._commands = args

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._state = True
        self._output = subprocess.run(self._commands, *args, **kwargs, **self._memory)
        return self._output


class Workspace(Subprocess):
    def __init__(self, workspace: str, os: str, *args: Any, **kwargs: Any):
        if os.lower() == "linux":
            super().__init__("wmctrl", "-s", workspace, *args, **kwargs)
        else:
            raise ValueError("Workspace is only available on Linux")
