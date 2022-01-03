from typing import List

from gurun.exceptions import RunnerException
from gurun.node import BranchNode, Node, NodeSet, NullNode
from gurun.utils import RaiseException, Sleep


class Runner(NodeSet):
    def __init__(
        self,
        nodes: List[Node],
        start_node: Node = None,
        end_node: Node = None,
        interval: int = 5,
        **kwargs,
    ) -> None:
        super().__init__(nodes, **kwargs)

        self._interval_node = Sleep(interval)
        self._start_node = BranchNode(
            NullNode() if start_node is None else start_node,
            negative=RaiseException(
                RunnerException("Could not successfully run start node")
            ),
        )
        self._end_node = BranchNode(
            NullNode() if end_node is None else end_node,
            negative=RaiseException(
                RunnerException("Could not successfully run end node")
            ),
        )

    def run(self, *args, **kwargs) -> None:
        self._start_node.run()

        try:
            while True:
                for node in self.nodes:
                    node.run()

                    self._interval_node.run()

        except KeyboardInterrupt:
            print("Interrupted!")

        self._end_node.run()
