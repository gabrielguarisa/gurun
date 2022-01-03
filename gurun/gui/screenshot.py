from typing import Any

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError(
        "cv2 is not installed. Please install it with `pip install opencv-python`."
    )

try:
    import mss
except ImportError:
    raise ImportError("mss is not installed. Please install it with `pip install mss`.")

try:
    import pyautogui
except ImportError:
    raise ImportError(
        "pyautogui is not installed. Please install it with `pip install pyautogui`."
    )

from gurun.node import Node


class ScreenshotPAG(Node):
    def run(self, filename: str = None, *args: Any, **kwargs: Any) -> np.ndarray:
        image = pyautogui.screenshot()

        if filename is not None:
            image.save(filename)

        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


class ScreenshotMMS(Node):
    def __init__(self, monitor: int = 0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._monitor = monitor

    def run(self, filename: str = None, *args: Any, **kwargs: Any) -> np.ndarray:
        with mss.mss() as sct:
            output = np.array(sct.grab(sct.monitors[self._monitor]))[:, :, :3]

        if filename is not None:
            cv2.imwrite(filename, output)

        return output
