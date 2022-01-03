from typing import Any

import random
import time

from gurun.node import Node, WrapperNode


class Sleep(WrapperNode):
    def __init__(self, interval: int = 5, **kwargs: Any):
        super().__init__(time.sleep, **kwargs)
        self._args_memory = (interval,)


class RaiseException(Node):
    def __init__(self, exception: Exception, **kwargs: Any):
        super().__init__(default_state=False, **kwargs)
        self._exception = exception

    def run(self, *args: Any, **kwargs: Any) -> None:
        raise self._exception


class Periodic(Node):
    def __init__(self, node: Node, interval: int, **kwargs: Any):
        super().__init__(**kwargs)
        self._node = node
        self._interval = interval
        self._last_run = 0

    def run(self, *args: Any, **kwargs: Any) -> Any:
        if time.time() - self._last_run < self._interval:
            self.state = False
            return None

        output = self._node.run(*args, **kwargs)
        self.state = self._node.state
        if self.state:
            self._last_run = time.time()

        return output


class RandomPeriodic(Periodic):
    def __init__(
        self,
        node: Node,
        min_interval: int,
        max_interval: int,
        **kwargs: Any,
    ):
        super().__init__(node, 0, **kwargs)
        self._min_interval = min_interval
        self._max_interval = max_interval

    def run(self, *args: Any, **kwargs: Any) -> Any:
        self._interval = random.randint(self._min_interval, self._max_interval)
        return super().run(*args, **kwargs)


class Wait(Node):
    def __init__(self, node: Node, timeout: int, **kwargs: Any):
        super().__init__(**kwargs)
        self._node = node
        self._timeout = timeout

    def run(self, *args: Any, **kwargs: Any) -> Any:
        start = time.time()
        while time.time() - start < self._timeout:
            self._node.run(*args, **kwargs)
            if self._node.state:
                self.state = True
                return self._node.output

        self.state = False
        return None


class NotNode(Node):
    def __init__(self, node: Node, **kwargs: Any):
        super().__init__(**kwargs)
        self._node = node

    def run(self, *args: Any, **kwargs: Any) -> bool:
        output = self._node.run(*args, **kwargs)
        self.state = not self._node.state
        return output


class While(Node):
    def __init__(self, trigger: Node, action: Node, timeout: int, **kwargs: Any):
        super().__init__(**kwargs)
        self._trigger = trigger
        self._action = action
        self._timeout = timeout

    def run(self, *args: Any, **kwargs: Any) -> None:
        start = time.time()
        self.state = False
        while time.time() - start < self._timeout:
            self._trigger.run(*args, **kwargs)
            if self._trigger.state:
                self._action.run(*args, **kwargs)
            else:
                self.state = True
                break


class Print(WrapperNode):
    def __init__(self, *values: Any, **kwargs: Any):
        super().__init__(print, **kwargs)
        self._args_memory = values
