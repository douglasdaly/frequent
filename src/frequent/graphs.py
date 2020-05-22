# -*- coding: utf-8 -*-
#
#   This module is part of the Frequent project, Copyright (C) 2020,
#   Douglas Daly.  The Frequent package is free software, licensed under
#   the MIT License.
#
#   Source Code:
#       https://github.com/douglasdaly/frequent-py
#   Documentation:
#       https://frequent-py.readthedocs.io/en/latest
#   License:
#       https://frequent-py.readthedocs.io/en/latest/license.html
#
"""
Graph data structures and utilities.

> This code was inspired by code in the
> `NetworkX <https://github.com/networkx/networkx/>`_ library.

"""
from abc import ABC
from collections.abc import Mapping
import typing as tp


class View(Mapping):
    """
    Class for viewing (but not modifying) Mapping-like data/objects.
    """
    __slots__ = (
        '_data',
    )

    def __init__(self, data: tp.Mapping[tp.Hashable, tp.Any]) -> None:
        self._data = data

    def __getstate__(self) -> tp.Dict[str, tp.Any]:
        return {'_data': self._data}

    def __setstate__(self, state: tp.Dict[str, tp.Any]) -> None:
        self._data = state['_data']

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> tp.Iterator[tp.Hashable]:
        return iter(self._data)

    def __getitem__(self, key: tp.Hashable) -> tp.Any:
        return self._data[key]

    def copy(self) -> 'View':
        return type(self)({k: v.copy() for k, v in self._data.items()})

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._data!r})'


class AdjacencyView(View):
    """
    Class for viewing a graph's adjacency data.
    """

    def __getitem__(self, key: tp.Hashable) -> tp.Any:
        return View(self._data[key])


class _NamedObject(ABC):
    """
    Abstract base class for named/identified objects.
    """
    __slots__ = (
        '_name',
    )

    def __init__(self, name: tp.Optional[str] = None) -> None:
        self._name = self._get_name(name=name)

    @property
    def name(self) -> str:
        """str: The name of this object."""
        return self._name

    def __str__(self) -> str:
        return self.name

    def _get_name(self, name: tp.Optional[str] = None) -> str:
        """Gets the name to use for this object from the given `name`.

        This method can be customized for user-defined naming
        conventions or automatic (re)naming or adjustments to the name,
        as needed.

        Parameters
        ----------
        name : str, optional
            The (input) name to use for getting the object's name.

        Returns
        -------
        str
            The name to use for the object.

        """
        return name or ''


class Node(_NamedObject):
    """
    Base class for graph Node objects.
    """
    __slots__ = (
        'data',
    )

    def __init__(
        self,
        name: tp.Optional[str] = None,
        **data: tp.Dict[str, tp.Any],
    ) -> None:
        self.data = data
        super().__init__(name=name)

    def __repr__(self) -> str:
        data = ', '.join(f"{k}={v!r}" for k, v in self.data.items())
        return f"{self.__class__.__name__}(name={self._name}, {data})"

    def __getitem__(self, key: tp.Hashable) -> tp.Any:
        return self.data[key]

    def __setitem__(self, key: tp.Hashable, value: tp.Any) -> None:
        self.data[key] = value

    def update(self, other: tp.Dict[tp.Hashable, tp.Any]) -> None:
        """Updates this node's ``data`` with the given `other` values.

        Parameters
        ----------
        other : Dict[Hashable, Any]
            The new data to update this object's ``data`` with.

        """
        self.data.update(other)


class Edge(Node):
    """
    Base class for graph Edge objects.
    """
    __slots__ = (
        'u',
        'v',
        'weight',
    )

    def __init__(
        self,
        u_of_edge: Node,
        v_of_edge: Node,
        weight: tp.Optional[float] = None,
        name: tp.Optional[str] = None,
        **data: tp.Dict[str, tp.Any],
    ) -> None:
        self.u = u_of_edge.name
        self.v = v_of_edge.name
        self.weight: float = weight or 1.0
        super().__init__(name=name, **data)

    def _get_name(self, name: tp.Optional[str] = None) -> str:
        return name or f"{self.u}-{self.v}"


class Graph(_NamedObject):
    """
    Base class for Graph objects.
    """
    __node_cls__: tp.Type[Node] = Node
    __edge_cls__: tp.Type[Edge] = Edge

    __slots__ = (
        '_adjs',
        '_nodes',
        'graph',
    )

    def __init__(
        self,
        data: tp.Optional[tp.Any] = None,
        name: tp.Optional[str] = None,
        **attrs: tp.Dict[str, tp.Any],
    ) -> None:
        self.graph = attrs
        self._nodes: tp.Dict[str, Node] = {}
        self._adjs: tp.Dict[str, tp.Dict[str, Edge]] = {}
        super().__init__(name=name)

    @property
    def adj(self) -> AdjacencyView:
        """AdjacencyView: A :obj:`View` of the graph's nodes and edges.
        """
        return AdjacencyView(self._adjs)

    @property
    def nodes(self) -> View:
        """View: A :obj:`View` of the graph's nodes."""
        return View(self._nodes)

    def __len__(self) -> int:
        """Gets the number of nodes in this graph."""
        return len(self._nodes)

    def __contains__(self, node: tp.Union[str, Node]) -> bool:
        """Returns ``True`` if the `node` is in this graph."""
        if isinstance(node, Node):
            node = node.name
        try:
            return node in self._nodes
        except TypeError:
            return False

    def __getitem__(self, node: str) -> View:
        """Returns a :obj:`View` of the nodes and associated :obj:`Edge`
        objects for the given `node`.
        """
        return self.adj[node]

    def add_node(
        self,
        node: tp.Union[str, Node],
        **data: tp.Dict[tp.Hashable, tp.Any]
    ) -> Node:
        """Adds a :obj:`Node` to this graph.

        Parameters
        ----------
        node : Union[str, Node]
            The :obj:`Node` object to add or the name of the new node to
            create and then add.
        data : optional
            The data to instantiate the new (or update the given `node`)
            with.

        Returns
        -------
        Node
            The newly-added (or existing, updated) :obj:`Node` object.

        """
        if not isinstance(node, Node):
            node = self.__node_cls__(name=node, **data)

        if node.name not in self._nodes:
            self._adjs[node.name] = {}
            self._nodes[node.name] = node
        else:
            self._nodes[node.name].update(data)

        return self._nodes[node.name]

    def remove_node(self, node: tp.Union[str, Node]) -> Node:
        """Removes a :obj:`Node` from this graph.

        Parameters
        ----------
        node : Union[str, Node]
            The node to remove from the graph.

        Returns
        -------
        Node
            The node removed from this graph.

        Raises
        ------
        KeyError
            If the `node` given is not contained in this graph.

        """
        if isinstance(node, Node):
            node = node.name
        if node not in self._nodes:
            raise KeyError(node)

        nbrs = list(self._adj[node])
        for u in nbrs:
            del self._adj[u][node]
        del self._adj[node]

        return self._nodes.pop(node)
