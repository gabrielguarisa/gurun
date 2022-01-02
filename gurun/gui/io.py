from typing import Any, Callable, List

import random

from gurun.node import Node, WrapperNode

try:
    import pyautogui
except ImportError:
    raise ImportError(
        "pyautogui is not installed. Please install it with `pip install pyautogui`."
    )


class Typewrite(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.typewrite, *args, **kwargs)


class Scroll(Node):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.scroll, *args, **kwargs)


class Click(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.click, *args, **kwargs)


class HotKey(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.hotkey, *args, **kwargs)


class MoveRel(Node):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._x = x
        self._y = y

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pyautogui.moveRel(self._x, self._y, **self._memory)


class MoveTo(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.moveTo, *args, **kwargs)


class DragRel(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.dragRel, *args, **kwargs)


class MultipleClicks(Click):
    def __call__(self, positions: List[List[int]], *args: Any, **kwargs: Any):
        for x, y in positions:
            super().__call__(*args, x=x, y=y, **kwargs)


class NaturalClick(Click):
    def __init__(
        self,
        easing_functions: List[Callable] = [
            pyautogui.easeInQuad,
            pyautogui.easeOutQuad,
            pyautogui.easeInOutQuad,
        ],
        minimum_duration: int = 1,
        maximum_duration: int = 1.5,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._easing_functions = easing_functions
        self._minimum_duration = minimum_duration
        self._maximum_duration = maximum_duration

    def __call__(self, *args: Any, **kwargs: Any):
        return super().__call__(
            *args,
            tween=random.choice(self._easing_functions),
            duration=random.uniform(self._minimum_duration, self._maximum_duration),
            **kwargs,
        )


class MultipleNaturalClicks(NaturalClick):
    def __call__(self, positions: List[List[int]], *args: Any, **kwargs: Any):
        for x, y in positions:
            super().__call__(*args, x=x, y=y, **kwargs)
