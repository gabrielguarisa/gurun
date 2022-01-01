from typing import Any, List

import random

from gurun.node import Node, WrapperNode

try:
    import pyautogui
except ImportError:
    raise ImportError(
        "pyautogui is not installed. Please install it with `pip install pyautogui`."
    )

pyautogui.FAILSAFE = False

MOUSE_RANDOM_MOVES = [
    pyautogui.easeInOutQuad,
    pyautogui.easeInOutCubic,
    pyautogui.easeInOutQuart,
    pyautogui.easeInOutQuint,
    pyautogui.easeInOutSine,
    pyautogui.easeInOutExpo,
    pyautogui.easeInOutCirc,
    pyautogui.easeInElastic,
    pyautogui.easeOutElastic,
    pyautogui.easeInOutElastic,
    pyautogui.easeInBounce,
    pyautogui.easeOutBounce,
    pyautogui.easeInOutBounce,
]
MINIMUM_DURATION = 0.1
MAXIMUM_DURATION = 1.0


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


class Move(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.move, *args, **kwargs)


class MoveTo(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.moveTo, *args, **kwargs)


class DragRel(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.dragRel, *args, **kwargs)


class MoveRel(WrapperNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(pyautogui.moveRel, *args, **kwargs)


class MultipleClicks(Click):
    def __call__(self, positions: List[List[int]], *args: Any, **kwargs: Any):
        for x, y in positions:
            super().__call__(*args, x=x, y=y, **kwargs, **self._memory)


class NaturalClick(Click):
    def __call__(self, *args: Any, **kwargs: Any):
        return super().__call__(
            *args,
            tween=random.choice(MOUSE_RANDOM_MOVES),
            duration=random.uniform(MINIMUM_DURATION, MAXIMUM_DURATION),
            **kwargs,
            **self._memory,
        )


class MultipleNaturalClicks(NaturalClick):
    def __call__(self, positions: List[List[int]], *args: Any, **kwargs: Any):
        for x, y in positions:
            super().__call__(*args, x=x, y=y, **kwargs, **self._memory)
