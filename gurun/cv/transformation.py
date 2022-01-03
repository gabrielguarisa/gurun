from typing import Any

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


class Transformation(Node):
    def run(self, detections: np.ndarray, *args: Any, **kwargs: Any) -> Any:
        if detections is None:
            self.state = False
            return None

        self.state = True
        return self._transform(detections, *args, **kwargs)

    def _transform(self, detections: np.ndarray, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()


class RectToPoint(Transformation):
    def _transform(self, detections: np.ndarray, *args: Any, **kwargs: Any) -> Any:
        if len(np.shape(detections)) == 1:
            return {
                "x": detections[0] + (detections[2] / 2),
                "y": detections[1] + (detections[3] / 2),
            }
        elif len(np.shape(detections)) == 2:
            return [[r[0] + (r[2] / 2), r[1] + (r[3] / 2)] for r in detections]
        else:
            raise ValueError(
                "RectToPoint: Input must be a 1D or 2D array. Input shape: {}".format(
                    np.shape(detections)
                )
            )


class NaturalRectToPoint(Transformation):
    def __init__(self, border_proportion: float = 0.25, **kwargs: Any):
        super().__init__(**kwargs)
        self._border_proportion = border_proportion

    def __natural_range(self, value: int, limit: int) -> int:
        value_start = value + (limit * self._border_proportion)
        value_end = (value + limit) - (limit * self._border_proportion)
        return math.floor(random.uniform(value_start, value_end))

    def _transform(self, detections: np.ndarray, *args: Any, **kwargs: Any) -> Any:
        if len(np.shape(detections)) == 1:
            return {
                "x": self.__natural_range(detections[0], detections[2]),
                "y": self.__natural_range(detections[1], detections[3]),
            }
        elif len(np.shape(detections)) == 2:
            return [
                [self.__natural_range(r[0], r[2]), self.__natural_range(r[1], r[3])]
                for r in detections
            ]
        else:
            raise ValueError(
                "NaturalRectToPoint: Input must be a 1D or 2D array. Input shape: {}".format(
                    np.shape(detections)
                )
            )


class Offset(Transformation):
    def __init__(self, xOffset: int = 0, yOffset: int = 0, **kwargs):
        super().__init__(**kwargs)
        self._xOffset = xOffset
        self._yOffset = yOffset

    def _transform(self, detections: np.ndarray, *args: Any, **kwds: Any) -> Any:
        if isinstance(detections, dict):
            return {
                "x": detections["x"] + self._xOffset,
                "y": detections["y"] + self._yOffset,
            }
        elif len(np.shape(detections)) == 1:
            detections[0] += self._xOffset
            detections[1] += self._yOffset
            return detections
        elif len(np.shape(detections)) == 2:
            for detection in detections:
                detection[0] += self._xOffset
                detection[1] += self._yOffset

            return detections
        else:
            raise ValueError(
                "Offset: Input must be a 1D or 2D array. Input shape: {}".format(
                    np.shape(detections)
                )
            )
