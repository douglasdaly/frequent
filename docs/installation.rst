############
Installation
############

The two primary methods for installing/using the functionality provided by the
:py:mod:`frequent` package: `installing the package <Package Installation>`_ or
copying the file(s) for the component(s) you need
(`vendorization <Vendorization>`_).  You can also install the latest version
`from source <Source Code>`_.


Package Installation
====================

To install :py:mod:`frequent` from the
`PyPI <https://pypi.org/project/frequent/>`_ package, using your package
manager of choice (in my case `Pipenv <https://docs.pipenv.org/en/latest/>`_):

.. code-block:: bash

    $ pipenv install frequent


Vendorization
=============

.. important::

    Be sure to attribute vendorized modules to this project by **not**
    modifying the headers of the copied files containing information about the
    the project.


Taking a cue from the excellent `boltons`_ package, each
component is self-contained in its respective file making this process simple.
Components are not dependent on one another and rely solely on the standard
Python library.  The unit tests for each module are similarly organized (though
written targeting `PyTest <https://docs.pytest.org/en/latest/>`_).  Just copy
the module(s) you need and (*optionally*) the associated ``test_<module>.py``
file(s) and you're good to go!


Source Code
===========

To install (or use the latest version) from source you can clone the Github
repository:

.. code-block:: bash

    $ git clone https://github.com/douglasdaly/frequent-py

The ``release`` branch *should* always represent the latest, unit-tested and
stable version of :py:mod:`frequent`.  For the latest development version see
the ``develop`` branch.

To install (in edit mode), once you've cloned the repository run:

.. code-block:: bash

    $ cd frequent-py/
    $ pipenv install -e .


.. _boltons: https://github.com/mahmoud/boltons
