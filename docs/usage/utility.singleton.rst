#########
Singleton
#########

This module provides a simple utility metaclass for creating singleton objects.


Usage
=====

Using the :obj:`Singleton <frequent.singleton.Singleton>` metaclass to make the
desired class a singleton is very easy:

.. code-block:: python

    from frequent.singleton import Singleton


    class MySingleton(object, metaclass=Singleton):

        def __init__(self, x):
            self.x = x


That's all there is to it.  Now the first call to ``MySingleton`` will create
(and store) the new object and subsequent calls will return the stored version:

>>> single = MySingleton(42)
>>> single.x
42
>>> other = MySingleton(0)
>>> other.x
42
>>> single.x = 0
>>> other.x
0
>>> other.x = 42
>>> single.x
42


Links
=====

API
---

Module
    :doc:`frequent.singleton <../api/frequent.singleton>`

Metaclasses
    :obj:`Singleton <frequent.singleton.Singleton>`
