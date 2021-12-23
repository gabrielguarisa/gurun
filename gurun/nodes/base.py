from typing import Any, Callable, List, Union


class Node:
    def __init__(
        self,
        name: str = None,
        default_state: bool = True,
        *args: Any,
        **kwargs: Any,
    ):
        self._name = self.__class__.__name__ if name is None else name
        self._state = default_state
        self._output = None
        self._memory = kwargs

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> bool:
        return self._state

    @property
    def output(self) -> Any:
        return self._output

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class NullNode(Node):
    def __init__(self, default_state: bool = True, *args: Any, **kwargs: Any):
        super().__init__(default_state=default_state, *args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        return None


class WrapperNode(Node):
    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._func = func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            self._output = self._func(*args, **kwargs, **self._memory)
            self._state = True
        except:
            self._output = None
            self._state = False
        return self._output


class SequentialNode(Node):
    def __init__(
        self,
        nodes: Union[Node, List[Node]] = [],
        ignore_none_output: bool = True,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.nodes = nodes
        self._ignore_none_output = ignore_none_output

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    @property
    def ignore_none_output(self) -> bool:
        return self._ignore_none_output

    @nodes.setter
    def nodes(self, nodes: Union[Node, List[Node]]) -> None:
        if isinstance(nodes, Node):
            nodes = [nodes]

        self._nodes = []
        for node in nodes:
            self.add_node(node)

    def add_node(self, node: Node) -> int:
        if not isinstance(node, Node):
            node = WrapperNode(node)

        self._nodes.append(node)
        return len(self._nodes) - 1

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"Running node: {self.name}")
        result = None
        first = True
        for node in self.nodes:
            print(f"Running node: {node.name}")
            if first:
                result = node(*args, **kwargs, **self._memory)
                first = False
            elif result is None and self.ignore_none_output:
                result = node(**self._memory)
            else:
                result = node(result, **self._memory)

            self._state = node.state
            self._output = node.output

            if not node.state:
                return self.output

        return self.output


class BranchNode(Node):
    def __init__(
        self,
        trigger: Node,
        positive: Node = NullNode(),
        negative: Node = NullNode(),
        ignore_none_output: bool = True,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.trigger = trigger
        self.positive = positive
        self.negative = negative
        self._ignore_none_output = ignore_none_output

    @property
    def trigger(self) -> SequentialNode:
        return self._trigger

    @property
    def positive(self) -> SequentialNode:
        return self._positive

    @property
    def negative(self) -> SequentialNode:
        return self._negative

    @property
    def ignore_none_output(self) -> bool:
        return self._ignore_none_output

    @trigger.setter
    def trigger(self, trigger: Node) -> None:
        if not isinstance(trigger, SequentialNode):
            trigger = SequentialNode(trigger)

        self._trigger = trigger

    @positive.setter
    def positive(self, positive: Node) -> None:
        if not isinstance(positive, SequentialNode):
            positive = SequentialNode(positive)

        self._positive = positive

    @negative.setter
    def negative(self, negative: Node) -> None:
        if not isinstance(negative, SequentialNode):
            negative = SequentialNode(negative)

        self._negative = negative

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        print(f"Running node: {self.name}")
        trigger_result = self.trigger(*args, **kwargs, **self._memory)

        if self.trigger.state:
            if trigger_result is None and self.ignore_none_output:
                self._output = self.positive(**self._memory)
            else:
                self._output = self.positive(trigger_result, **self._memory)
            self._state = self.positive.state
        else:
            if trigger_result is None and self.ignore_none_output:
                self._output = self.negative(**self._memory)
            else:
                self._output = self.negative(trigger_result, **self._memory)
            self._state = self.negative.state

        return self.output


class UnionNode(SequentialNode):
    def __init__(
        self,
        nodes: Union[Node, List[Node]] = [],
        return_node_name: Union[str, List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(nodes=nodes, *args, **kwargs)
        self._return_node_name = return_node_name

    @property
    def output(self) -> Any:
        if self._return_node_name is None or self._output is None:
            return self._output
        elif isinstance(self._return_node_name, str):
            if self._return_node_name not in self._output:
                return None
            return self._output[self._return_node_name]
        return {index: self._output[index] for index in self._return_node_name}

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        print(f"Running node: {self.name}")
        self._output = {}
        self._state = True
        for node in self.nodes:
            print(f"Running node: {node.name}")
            result = node(*args, **kwargs, **self._memory)

            if not (result is None and self.ignore_none_output):
                self._output[node.name] = result

            if not node.state:
                self._output = None
                self._state = False
                return None

        return self.output
