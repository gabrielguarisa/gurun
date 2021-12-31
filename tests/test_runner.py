from gurun.node import ConstantNode, NullNode
from gurun.runner import Runner
from gurun.utils import RaiseException


def test_runner():
    runner = Runner(
        [
            ConstantNode(1),
            ConstantNode(2),
            NullNode(),
            RaiseException(KeyboardInterrupt()),
        ],
        interval=0,
    )

    runner()

    assert runner.nodes[0].output == 1
    assert runner.nodes[1].output == 2
    assert runner.nodes[2].output is None

    assert len(runner.nodes) == 4
