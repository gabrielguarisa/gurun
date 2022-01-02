from typing import Any

import random
import time

from gurun.node import Node, WrapperNode


class Sleep(Node):
    def __init__(self, interval: int = 5, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._interval = interval

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        time.sleep(self._interval)


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


class RandomPeriodic(Periodic):
    def __init__(
        self,
        node: Node,
        min_interval: int,
        max_interval: int,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(node, 0, *args, **kwargs)
        self._min_interval = min_interval
        self._max_interval = max_interval

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._interval = random.randint(self._min_interval, self._max_interval)
        return super().__call__(*args, **kwargs)


class Wait(Node):
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


class NotNode(Node):
    def __init__(self, node: Node, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._node = node

    def __call__(self, *args: Any, **kwargs: Any) -> bool:
        self._output = self._node(*args, **kwargs, **self._memory)
        self._state = not self._node.state
        return self.output


class While(Node):
    def __init__(
        self, trigger: Node, action: Node, timeout: int, *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self._trigger = trigger
        self._action = action
        self._timeout = timeout

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        start = time.time()
        self._state = False
        while time.time() - start < self._timeout:
            self._trigger(*args, **kwargs, **self._memory)
            if self._trigger.state:
                self._action(*args, **kwargs, **self._memory)
            else:
                self._state = True
                break


class Print(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(print, *args, **kwargs)
        self._args = args

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return super().__call__(*self._args, *args, **kwargs)
