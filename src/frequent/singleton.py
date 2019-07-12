# -*- coding: utf-8 -*-
#
#   This module is part of the frequent project:
#       https://github.com/douglasdaly/frequent-py
#
"""
Singleton utility metaclass.
"""
from abc import ABC
from typing import Any
from typing import Mapping
from weakref import WeakValueDictionary


class Singleton(type):
    """
    Metaclass for singleton objects.

    Example
    -------
    This class is easy to use:

    .. code-block:: python

        class MyClass(SomeBaseClass, metaclass=Singleton):

            def __init__(self, x: int) -> None:
                self.x = x
                return

    Note the behavior of subsequent calls:

    >>> my_instance = MyClass(42)
    >>> my_instance.x
    42
    >>> another_instance = MyClass(43)
    >>> another_instance.x
    42

    Note that values set in subsequent calls to `__init__` will have no
    effect on the attribute.  To change the attribute do so on any of
    the instances:

    >>> another_instance.x = 43
    >>> my_instance.x
    43
    >>> my_instance.x = 42
    >>> another_instance.x
    42

    """
    __instances = WeakValueDictionary()

    def __call__(cls: type, *args, **kwargs) -> None:
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
        return cls.__instances[cls]
