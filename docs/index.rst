########
Frequent
########

.. toctree::
    :caption: Usage
    :maxdepth: 2
    :hidden:

    installation
    usage/main


.. toctree::
    :caption: Reference
    :maxdepth: 1
    :hidden:

    api/modules
    contributing
    conduct
    authors
    development/development.main
    changelogs/changelogs
    license


*Frequently used components for Python projects.*

|pypi| |nbsp| |travis| |nbsp| |cov| |nbsp| |docs| |nbsp| |pyvers|


About
=====

I found myself copying/re-writing certain components for my projects over and
over again.  This library is an attempt to take some of these components I find
myself needing frequently (and re-writing *too frequently*) and package them up
in a convenient and easy-to-use format.


Features
--------

All of the components in :py:mod:`frequent` have extensive
:doc:`code documentation <api/modules>` (as well as extensive
:doc:`usage documentation <usage/main>` and examples) and unit tests.  The
modules (and their associated unit tests) are entirely self-contained and
depend solely on the standard library.

- :doc:`config <usage/component.config>`: components providing global
  application configuration settings management and storage.

- :doc:`messaging <usage/foundation.messaging>`: the foundations for building
  custom messaging frameworks.

- :doc:`repository <usage/pattern.repository>`: base class (and exception
  classes) for implementing the repository pattern for back-end agnostic object
  storage.

- :doc:`singleton <usage/utility.singleton>`: metaclass for creating singleton
  classes.

- :doc:`unit_of_work <usage/pattern.unit_of_work>`: base classes for
  implementing the unit of work pattern for transactional blocks.


.. warning::

    This library is *currently* only compatible with Python 3.7, efforts are
    being made to make as much of it (as possible) compatible with 3.6 and 3.5.
    It will **not** be made compatible with Python 2.


Installation
============

You have a two options for installing/using `frequent`.  The first is to
install it the normal way, using your package manager of choice (`pipenv` for
instance):

.. code-block:: bash

    $ pipenv install frequent

The second way is via vendorizing the module(s) you need by copying the file(s)
for the module(s) you want directly into your project.  See the
:doc:`installation guide <installation>` for more details.


Contributing
============

Contributions to this project are welcome - and credit will always be given via
the project's ``AUTHORS`` file.  For details on contributing see the
:doc:`contribution guide <contributing>`.


License
=======

This project is Copyright |copy| 2019 by Douglas Daly.  This software is free
software, licensed under the :doc:`MIT License <license>`.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |pyvers| image:: https://img.shields.io/pypi/pyversions/frequent.svg
    :target: https://pypi.org/project/frequent/
    :alt: Supported Python Versions
.. |pypi| image:: https://img.shields.io/pypi/v/frequent.svg
    :target: https://pypi.org/project/frequent/
    :alt: PyPI Page
.. |docs| image:: https://readthedocs.org/projects/frequent-py/badge/?version=latest
    :target: https://frequent-py.readthedocs.io/en/latest/
    :alt: Documentation
.. |travis| image:: https://travis-ci.org/douglasdaly/frequent-py.svg?branch=master
    :target: https://travis-ci.org/douglasdaly/frequent-py
    :alt: Travis-CI
.. |cov| image:: https://coveralls.io/repos/github/douglasdaly/frequent-py/badge.svg
    :target: https://coveralls.io/github/douglasdaly/frequent-py
    :alt: Coverage
.. |nbsp| unicode:: 0xA0
    :trim:
.. |copy| unicode:: 0xA9 .. copyright sign
