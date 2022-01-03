from typing import Any, List, Union

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError(
        "cv2 is not installed. Please install it with `pip install opencv-python`."
    )

from gurun.node import Node


class TemplateDetection(Node):
    def __init__(
        self,
        target: Union[np.ndarray, str],
        threshold: float = 0.7,
        single_match: bool = False,
        method: int = cv2.TM_CCOEFF_NORMED,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if isinstance(target, str):
            target = cv2.imread(target)
            if target is None:
                raise ValueError(
                    f"Template Detection target file {target} does not exist"
                )

        self._target = target
        self._target_height = int(target.shape[0])
        self._target_width = int(target.shape[1])
        self._threshold = threshold
        self._single_match = single_match
        self._method = method

    def run(
        self, image: Union[np.ndarray, str], *args: Any, **kwargs: Any
    ) -> List[List[int]]:
        if isinstance(image, str):
            image = cv2.imread(image)
            if image is None:
                raise ValueError("Template Detection image file does not exist")

        result = cv2.matchTemplate(image, self._target, self._method)

        yloc, xloc = np.where(result >= self._threshold)

        rectangles = []
        for (x, y) in zip(xloc, yloc):
            rectangles.append([int(x), int(y), self._target_width, self._target_height])
            rectangles.append([int(x), int(y), self._target_width, self._target_height])

        rectangles, _ = cv2.groupRectangles(rectangles, 1, 0.2)

        if len(rectangles) == 0:
            self.state = False
            return None

        self.state = True
        return rectangles[0] if self._single_match else rectangles


class TemplateDetectionFrom(TemplateDetection):
    def __init__(
        self,
        source_node: Node,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._source_node = source_node

    def run(self, *args: Any, **kwargs: Any) -> List[List[int]]:
        image = self._source_node.run(*args, **kwargs)

        return super().run(image, *args, **kwargs)
