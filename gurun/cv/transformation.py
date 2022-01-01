from typing import Any, Dict, List

import math
import random

from gurun.node import Node

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError(
        "cv2 is not installed. Please install it with `pip install opencv-python`."
    )

BORDER_PROPORTION = 0.1


class RectToPoint(Node):
    def __call__(self, rect: np.ndarray, *args: Any, **kwargs: Any) -> Any:
        if len(np.shape(rect)) == 1:
            return {"x": rect[0] + (rect[2] / 2), "y": rect[1] + (rect[3] / 2)}
        elif len(np.shape(rect)) == 2:
            return [[r[0] + (r[2] / 2), r[1] + (r[3] / 2)] for r in rect]
        else:
            raise ValueError("RectToPoint: Input must be a 1D or 2D array")


class NaturalRectToPoint(Node):
    def __transform(self, value: int, limit: int) -> int:
        value_start = value + (limit * BORDER_PROPORTION)
        value_end = (value + limit) - (limit * BORDER_PROPORTION)
        return math.floor(random.uniform(value_start, value_end))

    def __call__(self, detections: np.ndarray, *args: Any, **kwargs: Any) -> Any:
        if detections is None:
            self._output = None
            self._state = False
            return None

        if len(np.shape(detections)) == 1:
            detections = {
                "x": self.__transform(detections[0], detections[2]),
                "y": self.__transform(detections[1], detections[3]),
            }
        elif len(np.shape(detections)) == 2:
            detections = [
                [self.__transform(r[0], r[2]), self.__transform(r[1], r[3])]
                for r in detections
            ]
        else:
            raise ValueError(
                "RectToPoint: Input must be a 1D or 2D array. Input shape: {}".format(
                    np.shape(detections)
                )
            )

        self._output = detections
        self._state = True

        return detections


class Offset(Node):
    def __init__(self, xOffset: int = 0, yOffset: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._xOffset = xOffset
        self._yOffset = yOffset

    def __call__(self, detections, *args: Any, **kwds: Any) -> Any:
        if detections is None:
            self._output = None
            self._state = False
            return None

        if len(np.shape(detections)) == 1:
            detections = {
                "x": detections["x"] + self._xOffset,
                "y": detections["y"] + self._yOffset,
            }
        elif len(np.shape(detections)) == 2:
            for detection in detections:
                detection[0] += self._xOffset
                detection[1] += self._yOffset

        self._output = detections
        self._state = True

        return detections
