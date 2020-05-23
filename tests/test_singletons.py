# -*- coding: utf-8 -*-
#
#   This module is part of the Frequent project, Copyright (C) 2019,
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
Unit tests for the singleton module.
"""
from typing import Optional

from frequent.singleton import Singleton


class BaseClass(object):

    def __init__(
        self, a: int, b: float, c: Optional[float] = None
    ) -> None:
        self.a = a
        self.b = b
        self.c = c or 0.0
        return


class SingleClass(BaseClass, metaclass=Singleton):

    def __init__(
        self, *args, d: Optional[float] = None, **kwargs
    ) -> None:
        self.d = d
        return super().__init__(*args, **kwargs)


class AnotherSingleClass(SingleClass):

    def __init__(self, *args, e: Optional[int] = 42, **kwargs):
        self.e = e
        return super().__init__(*args, **kwargs)


class SingletonTester(object):
    """
    Tests for the :obj:`Singleton` metaclass.
    """

    def test_is_singleton(self) -> None:
        sing_a = SingleClass(5, 4.0, d=3.2)
        sing_b = SingleClass(6, 5.0, c=2.3)
        assert id(sing_a) == id(sing_b)
        assert sing_a.a == 5
        assert sing_b.a == sing_a.a
        assert sing_b.b == 4.0
        assert sing_b.b == sing_a.b
        assert sing_b.c == 0.0
        assert sing_b.c == sing_a.c
        assert sing_b.d == 3.2
        assert sing_b.d == sing_a.d
        return

    def test_delete(self) -> None:
        sing_a = SingleClass(1, 2.0)
        sing_b = SingleClass(2.0, 4)
        assert id(sing_a) == id(sing_b)

        del sing_a
        del sing_b
        sing_c = SingleClass(3.0, 6)
        assert sing_c.a == 3.0
        assert sing_c.b == 6
        return

    def test_attributes(self) -> None:
        sing_a = SingleClass(1, 2.0)
        sing_b = SingleClass(2, 4.0)
        assert sing_b.a == 1
        sing_b.a = 2
        sing_a.b = 4.0
        assert sing_a.a == 2
        assert sing_b.b == 4.0
        return

    def test_inheritance(self) -> None:
        sing_a = SingleClass(1, 2.0)
        sing_o = AnotherSingleClass(2, 3.0, d=1.0)
        assert id(sing_a) != id(sing_o)
        assert type(sing_a) == SingleClass
        assert type(sing_o) == AnotherSingleClass
        assert sing_a.a == 1
        assert sing_o.a == 2
        assert not hasattr(sing_a, 'e')
        assert sing_o.e == 42
        return
