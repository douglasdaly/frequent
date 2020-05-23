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

> This code was inspired by, and borrows heavily from code found in the
> (excellent) `NetworkX <https://github.com/networkx/networkx/>`_
> project, for a more full-featured graph library check it out.

"""
from abc import ABC, ABCMeta
from collections.abc import Mapping, Set
import typing as tp

__all__ = [
    'AdjacencyView',
    'Edge',
    'EdgeDataView',
    'EdgeView',
    'Graph',
    'MapView',
    'Node',
    'NodeDataView',
    'NodeView',
    'View',
]


class View(ABC):
    """
    Abstract base class for viewing (but not modifying) data.
    """
    __slots__ = ()

    def __getstate__(self) -> tp.Dict[str, tp.Any]:
        ret = {}
        for n in self.__slots__:
            ret[n] = getattr(self, n)
        return ret

    def __setstate__(self, state: tp.Dict[str, tp.Any]) -> None:
        for n in self.__slots__:
            setattr(self, n, state[n])


class MapView(Mapping, View):
    """
    Class for viewing (but not modifying) Mapping-like data/objects.
    """
    __slots__ = (
        '_data',
    )

    def __init__(self, data: tp.Mapping[tp.Hashable, tp.Any]) -> None:
        self._data = data

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


class _NamedObject(object, metaclass=ABCMeta):
    """
    Abstract base class for named/identified objects.
    """
    __slots__ = (
        '_name',
    )

    def __init__(self, name: tp.Optional[tp.Hashable] = None) -> None:
        self._name = self._get_name(name=name)

    def __getstate__(self) -> tp.Dict[str, tp.Any]:
        return {'_name': self._name}

    def __setstate__(self, state: tp.Dict[str, tp.Any]) -> None:
        self._name = state['_name']

    @property
    def name(self) -> tp.Hashable:
        """Hashable: The name of this object."""
        return self._name

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        ret = f"{self.__class__.__name__}("
        if self.name is not None:
            return f"{ret}name={self.name!r})"
        return f"{ret})"

    def __eq__(self, other: tp.Any) -> bool:
        if not self._is_valid_operand(other):
            raise NotImplementedError
        return self.name == other.name

    def __lt__(self, other: tp.Any) -> bool:
        if not self._is_valid_operand(other):
            raise NotImplementedError
        return str(self.name) < str(other.name)

    def __hash__(self) -> int:
        return hash((type(self), self.name))

    def _is_valid_operand(self, other: tp.Any) -> bool:
        """Determines if the given `other` can be compared to this.

        Parameters
        ----------
        other : Any
            The other object to determine if it's able to be compared to
            this object.

        Returns
        -------
        bool
            Whether or not the two objects are comparable.

        """
        return isinstance(other, type(self)) or isinstance(self, type(other))

    def _get_name(self, name: tp.Optional[tp.Hashable] = None) -> tp.Hashable:
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
        return name


class _NamedDataObject(_NamedObject, metaclass=ABCMeta):
    """
    Abstract base class for objects with data dictionaries.
    """
    __slots__ = (
        '_data',
    )

    __view_cls__: tp.Type[View] = MapView

    def __init__(
        self,
        name: tp.Optional[str] = None,
        data: tp.Optional[tp.Dict[tp.Hashable, tp.Any]] = None,
    ) -> None:
        if data is None:
            data = {}
        self._data = data
        super().__init__(name=name)

    def __getstate__(self) -> tp.Dict[str, tp.Any]:
        ret = super().__getstate__()
        ret['_data'] = self._data
        return ret

    def __setstate__(self, state: tp.Dict[str, tp.Any]) -> None:
        super().__setstate__(state)
        self._data = state['_data']

    @property
    def data(self) -> View:
        """View: A :obj:`View` of the data stored on this object."""
        return self.__view_cls__(self._data)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.name}"

    def __repr__(self) -> str:
        return f"{self} {self._data!r}"

    def __eq__(self, other: tp.Any) -> bool:
        return super().__eq__(other) and self.data == other.data

    def __hash__(self) -> int:
        return super().__hash__()

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: tp.Hashable) -> bool:
        return key in self._data

    def __iter__(self) -> tp.Iterable[tp.Hashable]:
        return iter(self._data)

    def __getitem__(self, key: tp.Hashable) -> tp.Any:
        return self._data[key]

    def __setitem__(self, key: tp.Hashable, value: tp.Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: tp.Hashable) -> None:
        del self._data[key]

    def get(self, key: tp.Hashable, default: tp.Any = None) -> tp.Any:
        """Gets the data for the given `key` (if it exists).

        Parameters
        ----------
        key : Hashable
            The key to get the data for.
        default : Any, optional
            The value to return if no data exists for the given `key`
            (default is ``None``).

        Returns
        -------
        Any
            The value associated with the given `key` (or the `default`
            value given if said key doesn't exist).

        """
        if key in self._data:
            return self[key]
        return default

    def update(self, other: tp.Dict[tp.Hashable, tp.Any]) -> None:
        """Updates this object's ``data`` with the given `other` values.

        Parameters
        ----------
        other : Dict[Hashable, Any]
            The new data to update this object's ``data`` with.

        """
        self._data.update(other)


class Node(_NamedDataObject):
    """
    Graph Node
    """
    __slots__ = ()

    def __init__(
        self,
        name: tp.Hashable,
        **data: tp.Dict[tp.Hashable, tp.Any]
    ) -> None:
        super().__init__(name=name, data=data)


class Edge(_NamedDataObject):
    """
    Graph Edge
    """
    __separator__: str = '-'

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
        name: tp.Optional[tp.Hashable] = None,
        **data: tp.Dict[str, tp.Any],
    ) -> None:
        self.u = u_of_edge
        self.v = v_of_edge
        self.weight: float = 1.0 if weight is None else weight
        super().__init__(name=name, data=data)

    def _get_name(self, name: tp.Optional[tp.Hashable] = None) -> str:
        return name or f"{self.u.name} {self.__separator__} {self.v.name}"


class AdjacencyView(MapView):
    """
    Class for viewing a graph's adjacency data.
    """
    __view_cls__: tp.Type[View] = MapView

    def __getitem__(self, key: tp.Hashable) -> tp.Any:
        return self.__view_cls__(self._data[key])


class NodeDataView(Set):
    """
    View class for :obj:`Node` data.
    """
    __slots__ = (
        '_nodes',
        '_data',
        '_default',
    )

    def __init__(
        self,
        nodes: tp.Dict[tp.Hashable, Node],
        data: tp.Union[bool, str] = False,
        default: tp.Any = None
    ) -> None:
        self._nodes = nodes
        self._data = data
        self._default = default

    @classmethod
    def _from_iterable(
        cls,
        it: tp.Iterable[tp.Union[tp.Hashable, Node]]
    ) -> tp.Set[tp.Hashable]:
        return set(x.name if isinstance(x, Node) else x for x in it)

    def __str__(self) -> str:
        return str(list(self))

    def __repr__(self) -> str:
        if self._data is False:
            return f"{self.__class__.__name__}({tuple(self)})"
        elif self._data is True:
            return f"{self.__class__.__name__}({dict(self)})"
        return f"{self.__class__.__name__}({dict(self)}, data={self._data!r})"

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self) -> tp.Union[
        tp.Iterator[str],
        tp.Iterator[tp.Tuple[str, tp.Any]]
    ]:
        if self._data is False:
            return iter(self._nodes)
        elif self._data is True:
            return iter(self._nodes.items())
        return ((k, v.get(self._data, self._default))
                for k, v in self._nodes.items())

    def __contains__(
        self,
        key: tp.Union[
            tp.Union[tp.Hashable, Node],
            tp.Tuple[tp.Union[tp.Hashable, Node], tp.Hashable],
        ]
    ) -> bool:
        try:
            node, data = key
        except TypeError:
            node = key
            data = None
        if isinstance(node, Node):
            node = node.name
        if data is None:
            return node in self._nodes
        return node in self._nodes and self[node] == data

    def __getitem__(self, node: tp.Union[tp.Hashable, Node]) -> tp.Any:
        if isinstance(node, Node):
            node = node.name
        ret = self._nodes[node]
        if self._data is False:
            return ret
        elif self._data is True:
            return ret.data
        return ret.get(self._data, self._default)


class NodeView(Set, Mapping, View):
    """
    View class for :obj:`Node` objects.
    """
    __dataview_cls__: tp.Type[NodeDataView] = NodeDataView

    __slots__ = (
        '_nodes',
    )

    def __init__(self, graph: 'Graph') -> None:
        self._nodes = graph._nodes

    def __str__(self) -> str:
        return str(list(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({tuple(self)})"

    @classmethod
    def _from_iterable(
        cls,
        it: tp.Iterable[tp.Union[tp.Hashable, Node]]
    ) -> tp.Set[Node]:
        return set(x.name if isinstance(x, Node) else x for x in it)

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self) -> tp.Iterable[tp.Hashable]:
        return iter(self._nodes)

    def __getitem__(self, name: tp.Hashable) -> Node:
        return self._nodes[name]

    def __contains__(self, node: tp.Union[tp.Hashable, Node]) -> bool:
        if isinstance(node, Node):
            return node.name in self._nodes
        return node in self._nodes

    def __call__(
        self,
        data: tp.Union[bool, str] = False,
        default: tp.Any = None,
    ) -> NodeDataView:
        return self.data(data=data, default=default)

    def data(
        self,
        data: tp.Union[bool, str] = False,
        default: tp.Any = None,
    ) -> NodeDataView:
        """Gets a view for the nodes and their data.

        Parameters
        ----------
        data : Union[bool, str], optional
            Whether or not to include the data (if a ``bool`` value) or
            the specific data field to get a view for (if a ``str``).
        default : Any, optional
            If `data` is a specific field, the default value to return
            for nodes which don't have that field.

        Returns
        -------
        NodeDataView
            A data view for the nodes' data.

        """
        return self.__dataview_cls__(self._nodes, data=data, default=default)


class EdgeDataView(View):
    """
    Data view class for :obj:`Edge` object data.
    """
    __slots__ = (
        '_viewer',
        '_nodes',
        '_nodes_nbrs',
        '_data',
        '_default',
        '_report',
    )

    def __init__(
        self,
        viewer: 'EdgeView',
        nodes: tp.Optional[tp.Sequence[tp.Union[tp.Hashable, Node]]] = None,
        data: tp.Union[bool, str] = False,
        default: tp.Any = None,
    ) -> None:
        if nodes is not None:
            nodes = set(x.name if isinstance(x, Node) else x for x in nodes)
        self._viewer = viewer
        self._nodes = nodes
        self._data = data
        self._default = default
        if self._nodes is None:
            self._nodes_nbrs = self._viewer._adjs.items
        else:
            self._nodes_nbrs = lambda: [(x, self._viewer._adjs[x])
                                        for x in self._nodes]
        if self._data is True:
            self._report = lambda u, v, d: (u, v, d)
        elif self._data is False:
            self._report = lambda u, v, d: (u, v)
        else:
            self._report = lambda u, v, d: (
                u,
                v,
                d.get(self._data, self._default),
            )

    def __getstate__(self) -> tp.Dict[str, tp.Any]:
        return {
            'viewer': self._viewer,
            'nodes': self._nodes,
            'data': self._data,
            'default': self._default,
        }

    def __setstate__(self, state: tp.Dict[str, tp.Any]) -> None:
        self.__init__(**state)

    def __str__(self) -> str:
        return str(list(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self)})"

    def __len__(self) -> int:
        return sum(1 for e in self)

    def __iter__(self) -> tp.Iterable[tp.Union[
        tp.Tuple[tp.Hashable, tp.Hashable],
        tp.Tuple[tp.Hashable, tp.Hashable, tp.Any]]
    ]:
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr, data in nbrs.items():
                if nbr not in seen:
                    yield self._report(n, nbr, data)
            seen[n] = 1
        del seen

    def __contains__(
        self,
        key: tp.Union[
            tp.Tuple[tp.Hashable, tp.Hashable],
            tp.Tuple[tp.Hashable, tp.Hashable, tp.Any],
        ]
    ) -> bool:
        try:
            u, v = key[:2]
            data = self._viewer._adjs[u][v]
        except KeyError:
            try:
                data = self._viewer._adjs[v][u]
            except KeyError:
                return False
        return key == self._report(u, v, data)


class EdgeView(Set, Mapping, View):
    """
    View class for :obj:`Edge` objects.
    """
    __dataview_cls__: tp.Type[EdgeDataView] = EdgeDataView

    __slots__ = (
        '_adjs',
        '_graph',
    )

    def __init__(self, graph: 'Graph') -> None:
        self._graph = graph
        self._adjs = graph._adjs

    def __getstate__(self) -> tp.Dict[str, tp.Any]:
        return {'_graph': self._graph}

    def __setstate__(self, state: tp.Dict[str, tp.Any]) -> None:
        self._graph = state['_graph']
        self._adjs = self._graph._adjs

    def __str__(self) -> str:
        return str(list(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self)})"

    def __len__(self) -> int:
        n_nbrs = (len(nbrs) + (n in nbrs) for n, nbrs in self._adjs.items())
        return sum(n_nbrs) // 2

    def __iter__(self) -> tp.Iterable[tp.Tuple[tp.Hashable, tp.Hashable]]:
        seen = {}
        for n, nbrs in self._adjs.items():
            for nbr in list(nbrs):
                if nbr not in seen:
                    yield (n, nbr)
            seen[n] = 1
        del seen

    def __contains__(self, key: tp.Tuple[tp.Hashable, tp.Hashable]) -> bool:
        try:
            u, v = key
            return v in self._adjs[u] or u in self._adjs[v]
        except (KeyError, ValueError):
            return False

    def __getitem__(self, key: tp.Tuple[tp.Hashable, tp.Hashable]) -> Edge:
        u, v = key
        return self._adjs[u][v]

    def __call__(
        self,
        data: tp.Union[bool, str] = False,
        default: tp.Any = None,
        nodes: tp.Optional[tp.Sequence[tp.Union[tp.Hashable, Node]]] = None,
    ) -> EdgeDataView:
        return self.data(data=data, default=default, nodes=nodes)

    def data(
        self,
        data: tp.Union[bool, str] = False,
        default: tp.Any = None,
        nodes: tp.Optional[tp.Sequence[tp.Union[tp.Hashable, Node]]] = None,
    ) -> EdgeDataView:
        """Gets a data view for the :obj:`Edge` objects.

        Parameters
        ----------
        data : Union[bool, str], optional
        default : Any, optional
            The default value to use for edges which don't have the
            `data` field specified.
        nodes : Sequence[Union[Hashable, Node]], optional
            The node(s) to includes edges from in the view (default is
            ``None``, all nodes).

        Returns
        -------
        EdgeDataView
            The data view for the edges requested.

        """
        return self.__dataview_cls__(
            self,
            nodes=nodes,
            data=data,
            default=default,
        )


class Graph(_NamedObject):
    """
    Base class for Graph objects.
    """
    __node_cls__: tp.Type[Node] = Node
    __edge_cls__: tp.Type[Edge] = Edge
    __adj_view_cls__: tp.Type[AdjacencyView] = AdjacencyView
    __node_view_cls__: tp.Type[NodeView] = NodeView
    __edge_view_cls__: tp.Type[EdgeView] = EdgeView

    __slots__ = (
        '_adjs',
        '_nodes',
        'data',
    )

    def __init__(
        self,
        data: tp.Optional[tp.Any] = None,
        name: tp.Optional[str] = None,
        **attrs: tp.Dict[str, tp.Any],
    ) -> None:
        self.data = attrs
        self._nodes: tp.Dict[tp.Hashable, Node] = {}
        self._adjs: tp.Dict[tp.Hashable, tp.Dict[tp.Hashable, Edge]] = {}
        super().__init__(name=name)

    @property
    def adj(self) -> AdjacencyView:
        """AdjacencyView: A :obj:`View` of the graph's nodes and edges.
        """
        return self.__adj_view_cls__(self._adjs)

    @property
    def nodes(self) -> NodeView:
        """View: A :obj:`View` of the graph's nodes."""
        return self.__node_view_cls__(self)

    @property
    def edges(self) -> EdgeView:
        """View: A :obj:`View` of the graph's edges."""
        return self.__edge_view_cls__(self)

    def __len__(self) -> int:
        """Gets the number of nodes in this graph."""
        return len(self._nodes)

    def __contains__(self, node: tp.Union[tp.Hashable, Node]) -> bool:
        """Returns ``True`` if the `node` is in this graph."""
        if isinstance(node, Node):
            node = node.name
        try:
            return node in self._nodes
        except TypeError:
            return False

    def __getitem__(self, node: tp.Union[tp.Hashable, Node]) -> View:
        """Returns a :obj:`View` of the nodes and associated :obj:`Edge`
        objects for the given `node`.
        """
        if isinstance(node, Node):
            node = node.name
        return self.adj[node]

    def has_node(self, node: tp.Union[tp.Hashable, Node]) -> bool:
        """Checks if the specified node exists in this graph.

        Parameters
        ----------
        node : Union[Hashable, Node]
            The :obj:`Node` (or name of) to check for.

        Returns
        -------
        bool
            Whether or not this graph contains the specified node.

        """
        if isinstance(node, Node):
            node = node.name
        return node in self._nodes

    def add_node(
        self,
        node: tp.Union[tp.Hashable, Node],
        **data: tp.Dict[tp.Hashable, tp.Any]
    ) -> Node:
        """Adds a :obj:`Node` to this graph.

        Parameters
        ----------
        node : Union[Hashable, Node]
            The :obj:`Node` object to add, or the name of the new node
            to create and add.
        data : optional
            The data to instantiate the new (or update the given `node`)
            with.

        Returns
        -------
        Node
            The newly-added (or existing & updated) :obj:`Node` object.

        """
        if self.has_node(node):
            node = node.name if isinstance(node, Node) else node
            node = self._nodes[node]
            node.update(data)
        else:
            if not isinstance(node, Node):
                node = self.__node_cls__(node, **data)
            node = self._add_node_object(node)
        return node

    def _add_node_object(self, node: Node) -> Node:
        self._adjs[node.name] = {}
        self._nodes[node.name] = node
        return node

    def remove_node(self, node: tp.Union[tp.Hashable, Node]) -> Node:
        """Removes a :obj:`Node` from this graph.

        Parameters
        ----------
        node : Union[Hashable, Node]
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
        if not self.has_node(node):
            raise KeyError(node)
        return self._remove_node_object(node)

    def _remove_node_object(self, name: tp.Hashable) -> Node:
        nbrs = list(self._adj[name])
        for u in nbrs:
            del self._adj[u][name]
        del self._adj[name]
        return self._nodes.pop(name)

    def has_edge(
        self,
        u_of_edge: tp.Union[tp.Hashable, Node],
        v_of_edge: tp.Union[tp.Hashable, Node],
    ) -> bool:
        """Checks if the specified edge exists in this graph.

        Parameters
        ----------
        u_of_edge : Union[str, Node]
            The :obj:`Node` object (or name of) which the edge connects.
        v_of_edge : Union[str, Node]
            The :obj:`Node` object (or name of) which the edge connects.

        Returns
        -------
        bool
            Whether or not this graph contains the specified edge
            connection.

        """
        if isinstance(u_of_edge, Node):
            u_of_edge = u_of_edge.name
        if isinstance(v_of_edge, Node):
            v_of_edge = v_of_edge.name

        if u_of_edge not in self._adjs:
            return False
        return v_of_edge in self._adjs[u_of_edge]

    def add_edge(
        self,
        u_or_edge: tp.Union[tp.Hashable, Node, Edge],
        v_of_edge: tp.Optional[tp.Union[tp.Hashable, Node]] = None,
        weight: tp.Optional[float] = None,
        name: tp.Optional[tp.Hashable] = None,
        **data: tp.Dict[tp.Hashable, tp.Any],
    ) -> Edge:
        """Adds a new edge to this graph connecting the given nodes.

        Parameters
        ----------
        u_or_edge : Union[str, Node, Edge]
            The :obj:`Edge` object to add to this graph, or the
            :obj:`Node` object (or the name of either an existing one or
            one to create) to connect.
        v_of_edge : Union[str, Node], optional
            The other :obj:`Node` object (or the name of either an
            existing one or one to create) to connect (only required if
            `u_or_edge` is not an :obj:`Edge` object).
        weight : float, optional
            The weight to associate with this edge (if not provided the
            default value for the :obj:`Edge` class is used).
        name : str, optional
            The name to use for the new edge object (if not provided the
            edge's default is used).
        data : Dict[Hashable, Any], optional
            Any data to attach to the new edge object by passing to the
            constructor.

        Returns
        -------
        Edge
            The newly-created (or existing & updated) :obj:`Edge` object
            connecting nodes.

        """
        edge = None
        if isinstance(u_or_edge, Edge):
            edge = u_or_edge
            u = edge.u
            u_or_edge = u.name
            v = edge.v
            v_of_edge = v.name
        else:
            if v_of_edge is None:
                raise TypeError(
                    "add_edge() missing 1 required positional argument:"
                    " 'v_of_edge'"
                )
            if isinstance(u_or_edge, Node):
                u = self.add_node(u_or_edge)
                u_or_edge = u.name
            else:
                u = self._nodes.get(u_or_edge, self.add_node(u_or_edge))
            if isinstance(v_of_edge, Node):
                v = self.add_node(v_of_edge)
                v_of_edge = v.name
            else:
                v = self._nodes.get(v_of_edge, self.add_node(v_of_edge))

        if self.has_edge(u_or_edge, v_of_edge):
            edge = self._adjs[u_or_edge][v_of_edge]
            if weight is not None:
                edge.weight = weight
            edge.update(data)
        else:
            if edge is None:
                edge = self.__edge_cls__(
                    u,
                    v,
                    weight=weight,
                    name=name,
                    **data,
                )
            edge = self._add_edge_object(edge)
        return edge

    def _add_edge_object(self, edge: Edge) -> Edge:
        self._adjs[edge.u.name][edge.v.name] = edge
        self._adjs[edge.v.name][edge.u.name] = edge
        return edge

    def remove_edge(
        self,
        u_or_edge: tp.Union[tp.Hashable, Node, Edge],
        v_of_edge: tp.Optional[tp.Union[tp.Hashable, Node]] = None,
    ) -> Edge:
        """Removes a :obj:`Edge` from this graph.

        Parameters
        ----------
        u_or_edge : Union[Hashable, Node, Edge]
            The :obj:`Edge` object to remove from this graph, or the
            :obj:`Node` object (or name of) for the connection to
            remove.
        v_of_edge : Union[Hashable, Node], optional
            The :obj:`Node` object (or name of) for the connection to
            remove (only required if `u_or_edge` is not an :obj:`Edge`
            object).

        Returns
        -------
        Edge
            The :obj:`Edge` object removed from this graph.

        """
        edge = None
        if isinstance(u_or_edge, Edge):
            edge = u_or_edge
            u_or_edge = edge.u.name
            v_of_edge = edge.v.name
        else:
            if v_of_edge is None:
                raise TypeError(
                    "remove_edge() missing 1 required positional argument:"
                    " 'v_of_edge'"
                )
            if isinstance(u_or_edge, Node):
                u_or_edge = u_or_edge.name
            if isinstance(v_of_edge, Node):
                v_of_edge = v_of_edge.name

        if not self.has_edge(u_or_edge, v_of_edge):
            raise KeyError(
                f"{u_or_edge} {self.__edge_cls__.__separator__} {v_of_edge}"
            )
        return self._remove_edge_object(u_or_edge, v_of_edge)

    def _remove_edge_object(
        self,
        u_of_edge: tp.Hashable,
        v_of_edge: tp.Hashable
    ) -> Edge:
        edge = self._adjs[u_of_edge].pop(v_of_edge)
        if u_of_edge != v_of_edge:
            del self._adjs[v_of_edge][u_of_edge]
        return edge

    def clear(self) -> None:
        """Removes all the nodes, edges, and data for this graph.
        """
        self._adjs.clear()
        self._nodes.clear()
        self.data.clear()
