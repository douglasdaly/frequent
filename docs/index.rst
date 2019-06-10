########
Frequent
########

*Frequently used components for Python projects.*
|pypi| |nbsp| |travis| |nbsp| |cov| |nbsp| |docs| |nbsp| |pyvers|


About
=====

I found myself copying/re-writing certain components for my projects
over and over again.  This library is an attempt to take some of the
components I find myself needing frequently and package them up in a
convenient and easy-to-use manner.

Features
--------

- ``config`` for global configuration/settings management.


Installation
============

You have a few options for installing/using `frequent`.  The first is to
install using your package manager of choice, `pipenv` for instance:

.. code-block:: bash

    $ pipenv install frequent


However, taking a cue from the excellent `boltons`_ package, each
component is self-contained in its respective file/folder allowing for
easy vendorization.  Components are not dependent on one another and
rely solely on the standard library.  This makes vendorization of a
component as simple as copying just the file/folder for the component(s)
that you need.

.. _boltons: https://github.com/mahmoud/boltons


Contents
========

.. toctree::
    :maxdepth: 2
    :caption: Usage
    :hidden:


.. toctree::
    :maxdepth: 2
    :caption: Reference
    :hidden:

    api/modules
    contributing
    conduct
    authors
    development/development.main
    changelogs/changelogs
    license


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |pyvers| image:: https://img.shields.io/pypi/pyversions/frequent.svg
    :target: https://pypi.org/projects/frequent/
    :alt: Supported Python Versions
.. |pypi| image:: https://img.shields.io/pypi/v/frequent.svg
    :target: https://pypi.org/projects/frequent/
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
