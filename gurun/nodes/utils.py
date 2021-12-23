from typing import Any

import time

from gurun.nodes import Node


class Wait(Node):
    def __init__(self, seconds: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._seconds = seconds

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        time.sleep(self._seconds)


class RaiseException(Node):
    def __init__(self, exception: Exception, *args: Any, **kwargs: Any):
        super().__init__(default_state=False, *args, **kwargs)
        self._exception = exception

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        raise self._exception


class Periodic(Node):
    def __init__(self, node: Node, interval: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._node = node
        self._interval = interval
        self._last_run = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if time.time() - self._last_run < self._interval:
            self._state = False
            return None

        self._output = self._node(*args, **kwargs, **self._memory)
        self._state = self._node.state
        if self.state:
            self._last_run = time.time()

        return self._output


class WaitFor(Node):
    def __init__(self, node: Node, timeout: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._node = node
        self._timeout = timeout

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        start = time.time()
        while time.time() - start < self._timeout:
            self._node(*args, **kwargs, **self._memory)
            if self._node.state:
                self._state = True
                self._output = self._node.output
                return self._node.output

        self._state = False
        return None


class SaveInNodeMemory(Node):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._memory = {**self._memory, **kwargs}


class ClearNodeMemory(Node):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._memory = {}
