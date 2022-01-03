from typing import Any, Callable, List, Union

import os

from gurun.exceptions import GurunTypeError


class _BaseNode(object):
    def __init__(
        self,
        *,
        default_output: Any = None,
        default_state: bool = True,
        verbose: int = None,
        name: str = None,
        ravel: bool = False,
        **memory: Any,
    ) -> None:
        self.__output = default_output
        self.state = default_state
        self.verbose = verbose
        self.name = name
        self.ravel = ravel
        self._memory = memory
        self._args_memory = ()

    @property
    def output(self) -> Any:
        return self.__output

    @property
    def state(self) -> bool:
        return self.__state

    @state.setter
    def state(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise GurunTypeError(
                var_name="state", expected_type="bool", received_type=type(value)
            )

        self.__state = value

    @property
    def verbose(self) -> int:
        return self.__verbose

    @verbose.setter
    def verbose(self, value: int) -> None:
        if value is not None and not isinstance(value, int):
            raise GurunTypeError(
                var_name="verbose", expected_type="int", received_type=type(value)
            )

        self.__verbose = int(os.getenv("GURUN_VERBOSE", 0)) if value is None else value

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if value is not None and not isinstance(value, str):
            raise GurunTypeError(
                var_name="name", expected_type="str", received_type=type(value)
            )

        self.__name = self.__class__.__name__ if value is None else value

    @property
    def ravel(self) -> bool:
        return self.__ravel

    @ravel.setter
    def ravel(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise GurunTypeError(
                var_name="ravel", expected_type="bool", received_type=type(value)
            )

        self.__ravel = value

    def _run(self, m: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.verbose > 0:
                print(f"Running: {self.name}")
                if self.verbose > 2:
                    print(
                        f"\tArgs: {args}",
                        f"Kwargs: {kwargs}",
                        f"Memory: {self._memory}",
                        f"Args Memory: {self._args_memory}",
                    )

            self.__output = m(*self._args_memory, *args, **self._memory, **kwargs)

            if self.verbose > 1:
                print(f"\tOutput: {self.__output}")

            return self.__output

        return wrapper


class Node(_BaseNode):
    def __getattribute__(self, attr):
        attribute = super().__getattribute__(attr)

        if attr == "run":
            return self._run(attribute)

        return attribute

    def run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class ConstantNode(Node):
    def __init__(self, default_output: Any, **kwargs: Any) -> None:
        super().__init__(default_output=default_output, **kwargs)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        return self.output


class NullNode(ConstantNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(default_output=None, *args, **kwargs)


class WrapperNode(Node):
    def __init__(self, func: Callable, **kwargs: Any):
        super().__init__(**kwargs)
        self._func = func

    def run(self, *args: Any, **kwargs: Any) -> Any:
        try:
            self.state = True
            return self._func(*args, **kwargs)
        except:
            self.state = False


class NodeSet(Node):
    def __init__(
        self,
        nodes: Union[Node, List[Node]] = [],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
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

    def run(self, *args: Any, **kwargs: Any) -> None:
        for node in self.nodes:
            node.run()


class NodeSequence(NodeSet):
    def __init__(
        self,
        nodes: Union[Node, List[Node]] = [],
        ignore_none_output: bool = True,
        **kwargs: Any,
    ):
        super().__init__(nodes, **kwargs)
        self.ignore_none_output = ignore_none_output

    @property
    def ignore_none_output(self) -> bool:
        return self._ignore_none_output

    @ignore_none_output.setter
    def ignore_none_output(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise GurunTypeError(
                var_name="ignore_none_output",
                expected_type="bool",
                received_type=type(value),
            )

        self._ignore_none_output = value

    def run(self, *args: Any, **kwargs: Any) -> Any:
        output = None
        first = True
        ravel = False
        for node in self.nodes:
            if first:
                output = node.run(*args, **kwargs)
                first = False
            elif output is None and self.ignore_none_output:
                output = node.run()
            elif ravel:
                output = node.run(**output)
            else:
                output = node.run(output)

            self.state = node.state
            ravel = node.ravel

            if not node.state:
                return output

        return output


class UnionNode(NodeSequence):
    def __init__(
        self,
        nodes: Union[Node, List[Node]] = [],
        return_node_names: Union[str, List[str]] = None,
        **kwargs: Any,
    ):
        super().__init__(nodes=nodes, **kwargs)
        self.return_node_names = return_node_names

    @property
    def return_node_names(self) -> List[Node]:
        return self._return_node_names

    @return_node_names.setter
    def return_node_names(self, return_node_names: Union[str, List[str]]) -> None:
        if isinstance(return_node_names, str):
            return_node_names = [return_node_names]

        self._return_node_names = return_node_names

    def run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        output = {}
        self.state = True
        for node in self.nodes:
            result = node.run(*args, **kwargs)

            if not (result is None and self.ignore_none_output):
                output[node.name] = result

            if not node.state:
                output = None
                self.state = False
                return None

        if self.return_node_names is None:
            return output
        elif len(self.return_node_names) == 1:
            if self.return_node_names[0] not in output:
                return None
            return output[self.return_node_names[0]]
        return {index: output[index] for index in self.return_node_names}


class BranchNode(Node):
    def __init__(
        self,
        trigger: Node,
        positive: Node = None,
        negative: Node = None,
        ignore_none_output: bool = True,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.trigger = trigger
        self.positive = positive
        self.negative = negative
        self.ignore_none_output = ignore_none_output

    @property
    def trigger(self) -> Node:
        return self._trigger

    @trigger.setter
    def trigger(self, trigger: Node) -> None:
        if not isinstance(trigger, Node):
            trigger = WrapperNode(trigger)

        self._trigger = trigger

    @property
    def positive(self) -> Node:
        return self._positive

    @positive.setter
    def positive(self, value: Node) -> None:
        if value is None:
            value = NullNode()

        if not isinstance(value, Node):
            value = WrapperNode(value)

        self._positive = value

    @property
    def negative(self) -> Node:
        return self._negative

    @negative.setter
    def negative(self, value: Node) -> None:
        if value is None:
            value = NullNode()

        if not isinstance(value, Node):
            value = WrapperNode(value)

        self._negative = value

    @property
    def ignore_none_output(self) -> bool:
        return self._ignore_none_output

    @ignore_none_output.setter
    def ignore_none_output(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise GurunTypeError(
                var_name="ignore_none_output",
                expected_type="bool",
                received_type=type(value),
            )

        self._ignore_none_output = value

    def run(self, *args: Any, **kwargs: Any) -> Any:
        trigger_result = self.trigger.run(*args, **kwargs)

        if self.trigger.state:
            if trigger_result is None and self.ignore_none_output:
                output = self.positive.run()
            elif self.trigger.ravel:
                output = self.positive.run(**trigger_result)
            else:
                output = self.positive.run(trigger_result)
            self.state = self.positive.state
        else:
            if trigger_result is None and self.ignore_none_output:
                output = self.negative.run()
            elif self.trigger.ravel:
                output = self.negative.run(**trigger_result)
            else:
                output = self.negative.run(trigger_result)
            self.state = self.negative.state

        return output
