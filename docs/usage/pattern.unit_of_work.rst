############
Unit of Work
############

The :doc:`frequent.unit_of_work <../api/frequent.unit_of_work>` module provides
base classes for an implementation of the unit of work pattern.  This pattern
is (sometimes) used when working with object persistence/storage (e.g. ORMs).
The primary advantage of this pattern is the **transactional** nature of units
of work.  Regardless of the storage back-end implemented with the
:obj:`UnitOfWork <frequent.unit_of_work.UnitOfWork>` subclass (provided it can
support staging changes to be made, persisting those changes and deleting those
changes) all work performed inside a
:obj:`UnitOfWork <frequent.unit_of_work.UnitOfWork>` context block is a
transaction.

.. note::

    This pattern pairs well with the :doc:`pattern.repository` pattern and a
    command-based :doc:`foundation.messaging`.


Usage
=====

The abstract classes :obj:`UnitOfWork <frequent.unit_of_work.UnitOfWork>` and
:obj:`UnitOfWorkManager <frequent.unit_of_work.UnitOfWorkManager>` can be
extended to for specific use-cases.


Creating a UnitOfWork Subclass
------------------------------

The :obj:`UnitOfWork <frequent.unit_of_work.UnitOfWork>` class has two abstract
methods which need to be implemented in subclasses:

commit()
    Persists the changes made using the unit of work to the storage back-end.

rollback()
    Undo any changes made while using the unit of work and do not persist
    anything to the storage back-end.

A simple implementation might look like this:

.. code-block:: python

    from frequent.unit_of_work import UnitOfWork

    class MyUnitOfWork(UnitOfWork):

        def commit(self):
            # Code to persist changes
            return

        def rollback(self):
            # Code to dispose of changes
            return

If there's anything that needs to be done upon entering/exiting the
:obj:`UnitOfWork <frequent.unit_of_work.UnitOfWork>` context, you can customize
two additional methods:

.. code-block:: python

    class MyUnitOfWork(UnitOfWork):
        ...

        def __enter__(self):
            # Context entry setup code here
            return super().__enter__()

        def __exit__(self, exc_type, exc_value, traceback):
            # Pre commit/rollback teardown code here
            super().__exit__(exc_type, exc_value, traceback)
            # Post commit/rollback teardown code here
            return

.. warning::

    The order of the ``super()`` calls in the ``__enter__`` and ``__exit__``
    methods matters!

    In the ``__enter__`` call the superclass's method returns ``self`` (you
    could just return ``self`` if you wanted, though this approach ensures that
    any general entry-code that may exist in future versions of the base class
    will be executed).

    In the ``__exit__`` call the superclass's method will call either
    ``commit()`` or ``rollback()`` depending on the exit conditions.  So the
    location of that call matters and could vary depending on your particular
    use case.


Creating a UnitOfWorkManager Subclass
-------------------------------------

The :obj:`UnitOfWorkManager <frequent.unit_of_work.UnitOfWorkManager>` class
has a single abstract method to implement in subclasses:

start()
    This returns a new :obj:`UnitOfWork` instance, ready to use.

Continuing from the example above the associated
:obj:`UnitOfWorkManager <frequent.unit_of_work.UnitOfWorkManager>` class would
look something like:

.. code-block:: python

    from frequent.unit_of_work import UnitOfWorkManager

    class MyUnitOfWorkManager(UnitOfWorkManager):

        def start(self):
            return MyUnitOfWork()

The :obj:`UnitOfWorkManager <frequent.unit_of_work.UnitOfWorkManager>` class may
appear to be a useless abstraction from the above example (and in this case *it
kind of is*), but its usefulness can be seen in the (more realistic)
`extended example <Extended Example>`_ given below.


Using the UnitOfWork and Manager
--------------------------------

Now to use our new subclasses, remember the
:obj:`commit <frequent.unit_of_work.UnitOfWork.commit>` method will be called
upon exiting the context block (or the
:obj:`rollback <frequent.unit_of_work.UnitOfWork.rollback>` call if something
went wrong).  You're free to call
:obj:`commit <frequent.unit_of_work.UnitOfWork.commit>` at any point within the
block to persist any changes up to that point (if it makes sense for your
use-case).

>>> uowm = MyUnitOfWorkManager()
>>> with uowm.start() as uow:
...     # Code for doing work in this block
...     uow.commit()  # Persist changes up to this point (if you want/need to)
...     # More work code

.. important::

    You **do not** have to call the
    :obj:`commit <frequent.unit_of_work.UnitOfWork.commit>` method at the end
    of the ``with`` statement block, it will automatically be called upon a
    successful exit of the context.


Extended Example
================

Let's suppose we're using `SQLAlchemy's <https://www.sqlalchemy.org/>`_ ORM for
our storage back-end.  Then our unit of work class would look something like
this:

.. code-block:: python

    class MyUnitOfWork(UnitOfWork):

        def __init__(self, sessionmaker) -> None:
            self._sessionmaker = sessionmaker
            self.session = None
            return

        def __enter__(self):
            # Create a new session
            self.session = self._sessionmaker()
            return super().__enter__()

        def __exit__(self, exc_type, exc_value, traceback):
            super().__exit__(exc_type, exc_value, traceback)
            # Be sure to close the session when done, regardless
            self.session.close()
            self.session = None
            return

        def commit(self):
            self.session.commit()
            return

        def rollback(self):
            self.session.rollback()
            return


Now we'll instantiate the
:obj:`UnitOfWorkManager <frequent.unit_of_work.UnitOfWorkManager>` class to
spin-up new ``MyUnitOfWork`` instances to use:

.. code-block:: python

    class MyUnitOfWorkManager(UnitOfWorkManager):

        def __init__(self, sessionmaker):
            self._sessionmaker = sessionmaker
            return

        def start(self):
            return MyUnitOfWork(self._sessionmaker)


Lastly, let's wrap all our user management code inside another class whose sole
purpose is working with ``User`` (and other associated) objects.  We'll want
the ability to create users from this user manager class, but let's also
suppose that we also have a (separate) ``UserProfile`` object which stores some
basic information and settings about our users.  This object is always created
when we create our ``User`` objects.  This is where the advantage of the unit
of work pattern can really be seen:

.. code-block:: python

    class UserManager(object):

        def __init__(self, uow_manager):
            self.uowm = uow_manager
            return

        def create_user(self, name, email, location=None, receive_emails=True):
            with self.uowm.start() as uow:
                # Create and add the user
                user = User(name)
                uow.session.add(new_user)
                uow.session.flush()
                # Create and add the profile
                profile = UserProfile(user.id, email, location, receive_emails)
                uow.session.add(new_profile)
            return new_user


The above code demonstrates the advantages (`discussed earlier <advantages>`_)
of this design pattern.  In the above example if an error occurred at any point in creating
any new user (for example if we do some validation on the ``email`` or the user
already exists), the ``uow`` would have been rolled-back automatically and the
exception raised.  If everything works as expected then the ``uow`` will call
the ``commit()`` method and both the new user and profile objects will be
persisted to our storage back-end upon exiting the ``with`` context block.
Thus we  have only two possible outcomes when adding ``User`` objects:

 - **Both** the user *and their profile* are added to our system.
 - **Neither** the user *nor their profile* are added to our storage system.

The point is, we won't wind up in some in-between state where the user is added
but the associated profile is not (or vice-versa).


Useful Links
============

References
----------

- The unit of work pattern reference, originally from
  `Martin Fowler's <https://martinfowler.com/>`_
  `classic book <https://martinfowler.com/books/eaa.html>`_ on enterprise
  software architecture patterns:

    https://martinfowler.com/eaaCatalog/unitOfWork.html

- For an excellent overview and tutorial of this pattern in Python see this
  post (and the others in the series, as well as the examples in the
  `github repository <https://github.com/bobthemighty/blog-code-samples/tree/master/ports-and-adapters>`_)
  from `Bob Gregory <https://io.made.com/author/bob/>`_:

    https://io.made.com/repository-and-unit-of-work-pattern-in-python/


Frequent API
------------

Module
    :doc:`frequent.unit_of_work <../api/frequent.unit_of_work>`

Abstract Classes
    :obj:`UnitOfWork <frequent.unit_of_work.UnitOfWork>`,
    :obj:`UnitOfWorkManager <frequent.unit_of_work.UnitOfWorkManager>`
