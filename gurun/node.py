from typing import Any, Callable, List, Union


class Node:
    def __init__(
        self,
        default_output: Any = None,
        default_state: bool = True,
        name: str = None,
        ravel: bool = False,
        *args: Any,
        **kwargs: Any,
    ):
        self._output = default_output
        self._state = default_state
        self.name = name
        self.ravel = ravel
        self._memory = kwargs

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = self.__class__.__name__ if name is None else name

    @property
    def ravel(self) -> str:
        return self._ravel

    @ravel.setter
    def ravel(self, ravel: bool) -> None:
        self._ravel = ravel

    @property
    def state(self) -> bool:
        return self._state

    @property
    def output(self) -> Any:
        return self._output

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class NullNode(Node):
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        return None


class ConstantNode(Node):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._output


class WrapperNode(Node):
    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._func = func
        self.__call__.__func__.__doc__ = func.__doc__

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            self._output = self._func(*args, **kwargs, **self._memory)
            self._state = True
        except:
            self._output = None
            self._state = False
        return self._output


class NodeSet(Node):
    def __init__(
        self,
        nodes: Union[Node, List[Node]] = [],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.nodes = nodes

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Union[Node, List[Node]]) -> None:
        if isinstance(nodes, Node):
            nodes = [nodes]

        self._nodes = []
        for node in nodes:
            self.add_node(node)

    def add_node(self, node: Node, name: str = None) -> "NodeSet":
        if not isinstance(node, Node):
            node = WrapperNode(node)

        if name is not None:
            node.name = name

        self._nodes.append(node)
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        for node in self.nodes:
            print(f"Running: {node.name}")
            node()


class NodeSequence(NodeSet):
    def __init__(
        self,
        nodes: Union[Node, List[Node]] = [],
        ignore_none_output: bool = True,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(nodes, *args, **kwargs)
        self._ignore_none_output = ignore_none_output

    @property
    def ignore_none_output(self) -> bool:
        return self._ignore_none_output

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        result = None
        first = True
        ravel = False
        for node in self.nodes:
            print(f"Running: {node.name}")
            if first:
                result = node(*args, **kwargs, **self._memory)
                first = False
            elif result is None and self.ignore_none_output:
                result = node(**self._memory)
            elif ravel:
                result = node(**result, **self._memory)
            else:
                result = node(result, **self._memory)

            self._state = node.state
            self._output = node.output
            ravel = node.ravel

            if not node.state:
                return self.output

        return self.output


class UnionNode(NodeSequence):
    def __init__(
        self,
        nodes: Union[Node, List[Node]] = [],
        return_node_names: Union[str, List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(nodes=nodes, *args, **kwargs)
        self.return_node_names = return_node_names

    @property
    def return_node_names(self) -> List[Node]:
        return self._return_node_names

    @return_node_names.setter
    def return_node_names(self, return_node_names: Union[str, List[str]]) -> None:
        if isinstance(return_node_names, str):
            return_node_names = [return_node_names]

        self._return_node_names = return_node_names

    @property
    def output(self) -> Any:
        if self.return_node_names is None:
            return self._output
        elif len(self.return_node_names) == 1:
            if self.return_node_names[0] not in self._output:
                return None
            return self._output[self.return_node_names[0]]
        return {index: self._output[index] for index in self.return_node_names}

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        self._output = {}
        self._state = True
        for node in self.nodes:
            print(f"Running: {node.name}")
            result = node(*args, **kwargs, **self._memory)

            if not (result is None and self.ignore_none_output):
                self._output[node.name] = result

            if not node.state:
                self._output = None
                self._state = False
                return None

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
    def trigger(self) -> Node:
        return self._trigger

    @property
    def positive(self) -> Node:
        return self._positive

    @property
    def negative(self) -> Node:
        return self._negative

    @property
    def ignore_none_output(self) -> bool:
        return self._ignore_none_output

    @trigger.setter
    def trigger(self, trigger: Node) -> None:
        if not isinstance(trigger, Node):
            trigger = WrapperNode(trigger)

        self._trigger = trigger

    @positive.setter
    def positive(self, positive: Node) -> None:
        if not isinstance(positive, Node):
            positive = WrapperNode(positive)

        self._positive = positive

    @negative.setter
    def negative(self, negative: Node) -> None:
        if not isinstance(negative, Node):
            negative = WrapperNode(negative)

        self._negative = negative

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        trigger_result = self.trigger(*args, **kwargs, **self._memory)

        if self.trigger.state:
            if trigger_result is None and self.ignore_none_output:
                self._output = self.positive(**self._memory)
            elif self.trigger.ravel:
                self._output = self.positive(**trigger_result, **self._memory)
            else:
                self._output = self.positive(trigger_result, **self._memory)
            self._state = self.positive.state
        else:
            if trigger_result is None and self.ignore_none_output:
                self._output = self.negative(**self._memory)
            elif self.trigger.ravel:
                self._output = self.negative(**trigger_result, **self._memory)
            else:
                self._output = self.negative(trigger_result, **self._memory)
            self._state = self.negative.state

        return self.output
