import pytest

from gurun.node import (
    BranchNode,
    ConstantNode,
    Node,
    NodeSequence,
    NodeSet,
    NullNode,
    UnionNode,
    WrapperNode,
)


def test_node():
    node = Node(name="Test", default_state=False, default_output=True)
    assert node.name == "Test"
    assert node.state is False
    assert node.output is True

    with pytest.raises(NotImplementedError):
        node()


def test_null_node():
    node = NullNode()
    assert node.name == "NullNode"
    assert node.state is True
    assert node.output is None

    assert node() is None


def test_constant_node():
    node = ConstantNode(default_output=10)

    assert node.output == 10
    assert node.state is True
    assert node(1) == 10


def test_wrapper_node():
    def f(x: int) -> int:
        """Test docstring"""
        return x + 1

    node = WrapperNode(f)
    assert node.name == "WrapperNode"
    assert node.state is True
    assert node.output is None

    assert node(1) == 2
    assert node.__call__.__doc__ == "Test docstring"

    assert node.output == 2


def test_wrapper_node_with_exception():
    def f(x: int) -> int:
        raise Exception("Test")

    node = WrapperNode(f)
    assert node.name == "WrapperNode"
    assert node.state is True
    assert node.output is None

    assert node(1) == None

    assert node.output is None
    assert node.state is False


def test_node_set():
    node = NodeSet([NullNode(), lambda x: x + 1, lambda x: x + 2])

    assert node() is None
    assert node.state is True
    assert len(node.nodes) == 3


def test_empty_node_set():
    node = NodeSet()

    assert node() is None


def test_node_set_add_node():
    node = (
        NodeSet(NullNode())
        .add_node(WrapperNode(lambda x: x + 1))
        .add_node(lambda x: x + 2)
    )

    assert node() is None
    assert node.state is True
    assert len(node.nodes) == 3


def test_node_sequence():
    node = NodeSequence()

    node.add_node(NullNode())
    node.add_node(ConstantNode(default_output=10))
    node.add_node(lambda x: x + 1)

    assert node(1) == 11


def test_node_sequence_with_exception():
    def f(x: int) -> int:
        raise Exception("Test")

    node = NodeSequence()

    node.add_node(NullNode())
    node.add_node(f)

    assert node(1) is None


def test_union_node():
    node = (
        UnionNode()
        .add_node(NullNode())
        .add_node(lambda x: x + 1)
        .add_node(lambda x: x + 2, "TestNode")
    )

    assert node(1) == {"WrapperNode": 2, "TestNode": 3}

    node.return_node_names = ["TestNode", "WrapperNode"]

    assert node.output == {"TestNode": 3, "WrapperNode": 2}

    node.return_node_names = "WrapperNode"

    assert node.output == 2

    node.return_node_names = "Example"

    assert node.output == None


def test_union_node_with_exception():
    def f(x: int) -> int:
        raise Exception("Test")

    node = UnionNode().add_node(NullNode()).add_node(f)

    assert node(1) is None
    assert node.state is False


def test_branch_node():
    node = BranchNode(
        NullNode(),
        positive=ConstantNode(default_output=True),
        negative=ConstantNode(default_output=False),
    )

    assert node() == True
    assert node.trigger.state is True
    assert node.output == node.positive.output
    assert node.state is True

    node.trigger = NullNode(default_state=False)

    assert node() == False
    assert node.trigger.state is False
    assert node.output == node.negative.output
    assert node.state is True


def test_branch_node_with_wrappers():
    node = BranchNode(lambda x: x, positive=lambda x: x + 1, negative=lambda x: x - 1)

    assert node(0) == 1

    node.trigger = ConstantNode(default_output=0, default_state=False)

    assert node() == -1
