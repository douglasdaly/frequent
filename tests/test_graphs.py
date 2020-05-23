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
Unit tests for the graphs module.

> This code was inspired by, and uses code from the (excellent)
> `NetworkX <https://github.com/networkx/networkx/>`_ project, for a
> more full-featured graph library check it out.

"""
import pickle
import typing as tp

import pytest

import frequent.graphs as graphs


def pickle_tests(obj: tp.Any) -> bool:
    """Helper to test :obj:`pickle` use on the `obj` given."""
    for p in range(3, pickle.HIGHEST_PROTOCOL+1):
        pkl_obj = pickle.loads(pickle.dumps(obj, protocol=p))
        assert obj == pkl_obj
        assert isinstance(pkl_obj, type(obj))
        if hasattr(obj, '__slots__'):
            assert obj.__slots__ == pkl_obj.__slots__
    return True


class BaseView(graphs.View):
    """
    Helper class for testing :obj:`graphs.View`.
    """
    __slots__ = (
        'a',
        '_b',
    )

    def __init__(self, a: tp.Dict[str, int], b: float) -> None:
        self.a = a
        self._b = b

    @property
    def b(self) -> float:
        return self._b

    def __eq__(self, other: tp.Any) -> bool:
        if isinstance(other, type(self)):
            return self.a == other.a and self.b == other.b
        return False


class ViewTester(object):
    """
    Unit tests for the :obj:`graphs.View` class.
    """

    def setup(self) -> None:
        self.view = BaseView({'test': 1}, 1.2)

    def test_pickle(self) -> None:
        pickle_tests(self.view)


class MapViewTester(ViewTester):
    """
    Unit tests for the :obj:`graphs.MapView` class.
    """

    def setup(self) -> None:
        self.data = {
            0: {'color': 'blue', 'weight': 1.2},
            1: {},
            2: {'color': 1},
        }
        self.view = graphs.MapView(self.data)

    def test_len(self) -> None:
        assert len(self.view) == len(self.data)

    def test_iter(self) -> None:
        assert list(self.view) == list(self.data)

    def test_getitem(self) -> None:
        assert self.view[0] is self.data[0]
        assert self.view[2]['color'] == 1
        pytest.raises(KeyError, self.view.__getitem__, 3)

    def test_copy(self) -> None:
        v_copy = self.view.copy()
        assert isinstance(v_copy, type(self.view))
        assert v_copy[0] == self.view[0]
        assert v_copy == self.view
        assert v_copy[0] is not self.view[0]
        assert v_copy is not self.view

        assert not hasattr(self.view, '__setitem__')

    def test_items(self) -> None:
        assert sorted(self.view.items()) == sorted(self.data.items())

    def test_str(self) -> None:
        assert f"{self.view}" == f"{self.data}"

    def test_repr(self) -> None:
        assert repr(self.view) == f"{type(self.view).__name__}({self.data!r})"


class AdjacencyViewTester(MapViewTester):
    """
    Unit tests for the :obj:`graphs.AdjacenyView` object.
    """

    def setup(self) -> None:
        dd = {'color': 'blue', 'weight': 1.2}
        self.d = {0: dd, 1: {}, 2: {'color': 1}}
        self.data = {3: self.d, 0: {3: dd}, 1: {}, 2: {3: {'color': 1}}}
        self.view = graphs.AdjacencyView(self.data)

    def test_getitem(self):
        assert self.view[1] is not self.data[1]
        assert self.view[3][0] is self.view[0][3]
        assert self.view[2][3]['color'] == 1
        pytest.raises(KeyError, self.view.__getitem__, 4)

    def test_items(self) -> None:
        v_items = sorted((k, dict(v)) for k, v in self.view.items())
        assert v_items == sorted(self.view.items())


class SubNamed(graphs._NamedObject):
    """
    Helper class for testing :obj:`graphs._NamedObject`.
    """
    pass


class SubNamedChild(SubNamed):
    """
    Helper class for testing :obj:`graphs._NamedObject`.
    """
    pass


class SubNamedOther(graphs._NamedDataObject):
    """
    Helper class for testing :obj:`graphs._NamedObject`.
    """
    pass


class NamedObjectTester(object):
    """
    Unit tests for the :obj:`graphs._NamedObject` class.
    """

    def setup(self) -> None:
        self.default = SubNamed()
        self.named = SubNamed('Doug')
        self.child = SubNamedChild(self.named.name)
        self.other = SubNamedOther(self.named.name)

    def test_pickle(self) -> None:
        pickle_tests(self.default)
        pickle_tests(self.named)
        pickle_tests(self.child)
        pickle_tests(self.other)

    def test_name(self) -> None:
        assert self.default.name is None
        assert self.named.name == 'Doug'

        for obj in (self.default, self.named):
            try:
                obj.name = 'Liz'
                assert False
            except AttributeError:
                assert True

    def test_eq(self) -> None:
        assert self.default == self.default
        assert self.named == self.named
        assert self.default != self.named
        assert self.named == SubNamed(self.named.name)
        assert self.child == self.named
        assert self.named == self.child
        pytest.raises(NotImplementedError, self.named.__eq__, self.other)

    def test_lt(self) -> None:
        assert self.named < self.default
        assert not self.named < self.named
        pytest.raises(NotImplementedError, self.named.__lt__, self.other)

    def test_hash(self) -> None:
        assert hash(self.named) == hash((type(self.named), self.named.name))

    def test_is_valid_operand(self) -> None:
        assert self.default._is_valid_operand(self.default)
        assert self.default._is_valid_operand(self.named)
        assert self.named._is_valid_operand(self.default)
        assert self.named._is_valid_operand(self.child)
        assert self.child._is_valid_operand(self.named)
        assert not self.named._is_valid_operand(self.other)
        assert not self.other._is_valid_operand(self.named)

    def test_get_name(self) -> None:
        assert self.default._get_name() is None
        assert self.default._get_name('Liz') == 'Liz'

    def test_str(self) -> None:
        assert str(self.default) == str(self.default.name)
        assert str(self.named) == self.named.name

    def test_repr(self) -> None:
        assert (repr(self.named) ==
                f"{self.named.__class__.__name__}(name={self.named.name!r})")


class SubDataNamed(graphs._NamedDataObject):
    """
    Helper class for testing :obj:`graphs._NamedDataObject`.
    """
    pass


class NamedDataTester(object):
    """
    Unit tests for the :obj:`graphs._NamedDataObject` class.
    """

    def setup(self) -> None:
        self.data = {'a': 1, 'b': 2}
        self.default = SubDataNamed()
        self.obj_a = SubDataNamed(name='Data', data=self.data)
        self.obj_b = SubDataNamed(name='Data', data=self.data.copy())
        self.obj_c = SubDataNamed(name='Data')

    def test_pickle(self) -> None:
        pickle_tests(self.default)
        pickle_tests(self.obj_a)
        pickle_tests(self.obj_b)

    def test_data(self) -> None:
        assert self.default.data == {}
        assert isinstance(self.default.data, SubDataNamed.__view_cls__)

        assert self.obj_a.data == self.data
        assert self.obj_a.data is not self.data
        assert self.obj_a._data is self.data

        assert self.obj_b.data == self.data
        assert self.obj_b.data is not self.data
        assert self.obj_b._data is not self.data

        assert self.obj_c.data == self.default.data
        assert self.obj_c.data is not self.default.data

    def test_eq(self) -> None:
        assert self.obj_a != self.default
        assert self.obj_a == self.obj_b
        assert self.obj_b == self.obj_a
        assert self.obj_a is not self.obj_b
        assert self.obj_a != self.obj_c
        assert self.obj_c != self.obj_b
        assert self.obj_c != self.default

    def test_hash(self) -> None:
        assert hash(self.default) != hash(self.obj_a)
        assert hash(self.obj_a) == hash(self.obj_b)
        assert hash(self.obj_b) == hash(self.obj_c)

    def test_len(self) -> None:
        assert len(self.default) == 0
        assert len(self.obj_a) == len(self.data)

    def test_contains(self) -> None:
        assert 'a' not in self.default
        assert 'a' in self.obj_a
        assert 'b' in self.obj_b

    def test_iter(self) -> None:
        assert list(self.obj_a) == list(self.data)

    def test_getitem(self) -> None:
        assert self.obj_a['a'] == 1
        assert self.obj_b['b'] == 2
        pytest.raises(KeyError, self.default.__getitem__, 'a')

    def test_setitem(self) -> None:
        data = self.data.copy()

        obj = SubDataNamed(data=data.copy())
        assert obj['a'] == 1
        obj['a'] = 2
        assert obj['a'] == 2
        assert data['a'] == 1

        obj = SubDataNamed(data=data)
        obj['b'] = 3
        assert obj['b'] == 3
        assert obj['b'] == data['b']
        data['a'] = 2
        assert obj['a'] == 2

    def test_delitem(self) -> None:
        data = self.data.copy()

        obj = SubDataNamed(data=data.copy())
        assert 'a' in obj
        del obj['a']
        assert 'a' not in obj
        assert 'a' in data

        obj = SubDataNamed(data=data)
        assert 'b' in obj
        assert 'b' in data
        del obj['b']
        assert 'b' not in obj
        assert 'b' not in data
        assert 'a' in obj
        assert 'a' in data
        del data['a']
        assert 'a' not in obj

    def test_get(self) -> None:
        assert self.obj_a.get('a') == 1
        assert self.obj_a.get('x') is None
        assert self.obj_a.get('z', 5) == 5

    def test_update(self) -> None:
        obj = SubDataNamed(name='Data')
        assert obj == self.obj_c
        obj.update(self.data)
        assert obj.data == self.data
        assert obj.data is not self.data
        assert obj != self.obj_c

    def test_str(self) -> None:
        assert (str(self.obj_a) ==
                f"{self.obj_a.__class__.__name__}: {self.obj_a.name}")

    def test_repr(self) -> None:
        assert repr(self.obj_a) == f"{self.obj_a} {self.obj_a._data!r}"


class NodeTester(object):
    """
    Unit tests for the :obj:`graphs.Node` class.
    """

    def setup(self) -> None:
        self.node_a = graphs.Node('A', category=1)
        self.node_b = graphs.Node('B', category=1)

    def test_init(self) -> None:
        assert self.node_a.name == 'A'
        assert self.node_a.name != self.node_b.name

        assert self.node_a.data == self.node_b.data
        assert self.node_a._data is not self.node_b._data


class EdgeTester(object):
    """
    Unit tests for the :obj:`graphs.Edge` class.
    """

    def setup(self) -> None:
        self.u = graphs.Node('u')
        self.v = graphs.Node('v')

        self.edge = graphs.Edge(self.u, self.v)
        self.edge_weight = graphs.Edge(self.u, self.v, 1.2)
        self.edge_named = graphs.Edge(self.u, self.v, name='Custom')
        self.edge_data = graphs.Edge(self.u, self.v, category=1)

    def test_init(self) -> None:
        u = graphs.Node('u')
        v = graphs.Node('v')
        assert self.edge.u == u
        assert self.edge.u is not u
        assert self.edge.v == v
        assert self.edge.v is not v

        u = self.u
        v = self.v
        assert self.edge.u == u
        assert self.edge.u is u
        assert self.edge.v == v
        assert self.edge.v is v

        assert self.edge.weight == 1.0
        assert self.edge_weight.weight == 1.2
        assert self.edge.weight == self.edge_named.weight
        assert self.edge_named.weight == self.edge_data.weight

        assert self.edge.name == self.edge._get_name()
        assert self.edge.name == self.edge_weight.name
        assert self.edge_named.name == 'Custom'

        assert 'category' not in self.edge
        assert 'category' in self.edge_data
        assert self.edge_data['category'] == 1

    def test_get_name(self) -> None:
        assert (self.edge._get_name() ==
                f"{self.u.name} {self.edge.__separator__} {self.v.name}")
