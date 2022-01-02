"""Framework de autotomação de tarefas"""

import sys

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata  # pragma: no cover


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()

from gurun import exceptions, runner, utils
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

__all__ = [
    "version",
    "Node",
    "NullNode",
    "ConstantNode",
    "WrapperNode",
    "NodeSet",
    "NodeSequence",
    "UnionNode",
    "BranchNode",
    "exceptions",
    "runner",
    "utils",
]
