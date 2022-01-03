from gurun import Node

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError(
        "cv2 is not installed. Please install it with `pip install opencv-python`."
    )


class ForEachDetection(Node):
    def __init__(self, node: Node, **kwargs) -> None:
        super().__init__(**kwargs)
        self._node = node

    def run(self, detections: np.ndarray, *args, **kwargs) -> None:
        for detection in detections:
            self._node.run(detection, *args, **kwargs)
