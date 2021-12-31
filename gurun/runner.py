from typing import List

from gurun.exceptions import RunnerException
from gurun.node import BranchNode, Node, NodeSet, NullNode
from gurun.utils import RaiseException, Sleep


class Runner(NodeSet):
    def __init__(
        self,
        nodes: List[Node],
        start_node: Node = NullNode(),
        end_node: Node = NullNode(),
        interval: int = 5,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(nodes, *args, **kwargs)

        self._interval_node = Sleep(interval)
        self._start_node = BranchNode(
            start_node,
            negative=RaiseException(
                RunnerException("Could not successfully run start node")
            ),
        )
        self._end_node = BranchNode(
            end_node,
            negative=RaiseException(
                RunnerException("Could not successfully run end node")
            ),
        )

    def __call__(self):
        self._start_node()

        try:
            while True:
                for node in self.nodes:
                    node()

                    self._interval_node()

        except KeyboardInterrupt:
            print("Interrupted!")

        self._end_node()
