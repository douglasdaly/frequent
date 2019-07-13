##########
Repository
##########

The :doc:`frequent.repository <../api/frequent.repository>` module provides the
base class for implementing the repository pattern for object storage and
access.

- It **decouples** the storage-system logic/details of the back-end from the
  repository interface.  Allowing the ability to easily switch storage
  back-ends without requiring any changes to the business-logic.
- It allows you to store different types of objects in different storage
  back-ends but provides a **common interface** for working with all types of
  stored objects.

.. note::

    This pattern pairs well with the :doc:`pattern.unit_of_work` pattern and a
    command-based :doc:`foundation.messaging`.


Usage
=====

Using the :obj:`Repository` object requires a user-specific abstraction layer
(on top of the provided :obj:`Repository` abstraction) and then storage-system
specific implementations (called "adapters") which are actually used.

The :obj:`Repository` object has the following abstract methods:

add(obj)
    Adds a new object to the repository.

all()
    Returns an :obj:`Iterable` of all the objects stored in the repository.

_get(id, default=None)
    Gets the object in the repository stored with the given ``id``, if any,
    otherwise returns the ``default`` value given.

remove(id)
    Removes (and returns) the object stored in the repository with the ``id``
    given.  If no object exists for the given ``id`` an
    :obj:`ObjectNotFoundError` is thrown.

Additionally, the :obj:`Repository` specifies one concrete method:

get(id)
    Gets the object with the given ``id`` (via the :obj:`_get` method), throws
    an :obj:`ObjectNotFoundError` if no object exists for the given ``id``.


Creating the Repository Definition
----------------------------------

First we'll need to create an abstract subclass of the :obj:`Repository` object
which defines the methods which can be used by the business-logic to interact
with the repository.  For example, let's say we're creating a repository for
working with ``User`` objects:

.. code-block:: python

    from abc import ABCMeta, abstractmethod
    from frequent.repository import Repository


    class User(object):

        def __init__(self, name):
            self.name = name
            self.id = None
            return


    class UserRepository(Repository, metaclass=ABCMeta):

        def id_to_name(self, id):
            return self.get(id).name

        def name_to_id(self, name):
            return self.get_user_from_name(name).id

        @abstractmethod
        def get_user_from_name(name):
            pass

        @abstractmethod
        def change_user_name(old_name, new_name):
            pass


Above we specify that, in addition to the functionality specified by the
:obj:`Repository` base class (`see above <repo-functions>`_) we'll also have a
few additional functions for getting ``User`` objects and data.  Note how we've
specified **both** abstract and concrete methods - this allows us to
consolidate code where possible.  Since we specify an abstract method for
getting ``User`` objects by name, and the :obj:`Repository` base class
specifies the :obj:`get` (via the abstract :obj:`_get`) method for getting
users by their ID number we can write the implementations for the
``id_to_name`` and ``name_to_id`` methods in a concrete-manner.

.. note::

    To throw custom :obj:`ObjectNotFoundError` exceptions from your repository
    subclasses.  You can set the ``__obj_cls__`` class attribute on your
    :obj:`ObjectNotFoundError` subclass and then set the ``__not_found_ex__``
    class attribute on your :obj:`Repository` subclass:

    .. code-block:: python

        from frequent.repository import ObjectNotFoundError


        class UserNotFoundError(ObjectNotFoundError):
            __obj_cls__ = User


        class UserRepository(Repository):
            __not_found_ex__ = UserNotFoundError
            # The rest of your repository code here


Our ``UserRepository`` object specifies the functionality we require on for
working with the storage of ``User`` objects but not the details of how we
store them.  That's the second part, writing the *adapter*.

Creating an Adapter
-------------------

Let's suppose we're using
`SQLAlchemy's ORM <https://docs.sqlalchemy.org/en/13/orm/>`_ as our storage
back-end.  We can then write a concrete implementation adapter for our
``UserRepository`` using this back-end.  The code below implements *some* (not
all, for the sake of brevity) of the concrete methods required (assuming we've
setup our ``User`` class appropriately with the SQLAlchemy ORM):

.. code-block:: python

    class UserSqlAlchemyRepository(UserRepository):

        def __init__(self, sql_session):
            self._session = sql_session
            return

        def add(self, user):
            self._session.add(user)
            self._session.commit()
            return

        def all(self):
            return self._session.query(User).all()

        def _get(self, user_id, default=None):
            ret = self._session.query(User).filter_by(id=user_id).first()
            if ret is None:
                return default
            return ret

        def get_user_from_name(self, name):
            ret = self._session.query(User).filter_by(name=name).first()
            if not ret:
                raise ObjectNotFoundError(name, field='name')
            return ret

        ...

.. important::

    Whether or not the call raises an exception is up to you and your specific
    use-case.  You **should** always specify this in the abstract method's
    docstring and/or type annotations.


Using the Adapter
-----------------

Now that we've written our adapter class, we can use the ``UserRepository`` as
needed:

>>> session = my_sessionmaker()
>>> user_repo = UserSqlAlchemyRepository(session)
>>> new_user = User('Doug')
>>> print(new_user.id)
None
>>> user_repo.add(new_user)
>>> new_user.id
1
>>> user_repo.get_user_from_name('Doug')
User(id=1, name='Doug')
>>> user_repo.get(1)
User(id=1, name='Doug')
>>> user_repo.get(2)
Traceback (most recent call last):
  ...
ObjectNotFoundError: No object found for: id=2.

We could then write other adapters, for other storage back-ends, but interact
with them in the same way we did above.

.. note::

    We can see, from above, how this repository would work well with the
    :doc:`pattern.unit_of_work` pattern.  We'd remove the
    ``self._session.commit()`` call in the :obj:`add` method and call
    ``self._session.flush()`` instead.  Within our unit of work context block
    we'd perform all of our interactions with the session-based
    ``UserSqlAlchemyRepository`` object and then have the :obj:`UnitOfWork`
    call the ``session.commit()``.


Links
=====

References
----------

- The repository pattern reference, originally from
  `Martin Fowler's <https://martinfowler.com/>`_
  `classic book <https://martinfowler.com/books/eaa.html>`_ on enterprise
  software architecture patterns:

    https://martinfowler.com/eaaCatalog/repository.html

- For an excellent overview and tutorial of this pattern in Python see this
  post (and the others in the series, as well as the examples in the
  `github repository <https://github.com/bobthemighty/blog-code-samples/tree/master/ports-and-adapters>`_
  ) from `Bob Gregory <https://io.made.com/author/bob/>`_:

    https://io.made.com/repository-and-unit-of-work-pattern-in-python/


API
---

Module
    :doc:`frequent.repository <../api/frequent.repository>`

Abstract Classes
    :obj:`Repository <frequent.repository.Repository>`

Exceptions
    :obj:`RepositoryException <frequent.repository.RepositoryException>`,
    :obj:`ObjectNotFoundError <frequent.repository.ObjectNotFoundError>`
