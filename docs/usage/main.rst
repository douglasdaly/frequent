#######
Modules
#######

The :py:mod:`frequent` package provides helpful components and utilities which
are commonly used in larger projects.  Each is self-contained in a seperate
module.  These modules can be broadly divided into four categories:

- Full-fledged, ready-to-use implementations of frequently-used application
  `Components`_.
- Base components which lay the `Foundations`_ for frequently-used components,
  but require some customization prior to use.
- Abstract software design `Patterns`_ to be implemented for specific use
  cases.
- Useful and frequently-repeated `Utilities`_ to avoid re-writing boilerplate
  code time and time again.

Each of the modules is neatly packaged into a single-file which depends only on
the standard library and can be dragged-and-dropped into your application as
needed.  The associated unit tests for each module (written for
`PyTest <https://docs.pytest.org/en/latest/>`_), are also provided and, like
the components, are self-contained within the respective ``test_<module>``
files.  Everything is typed using the new :py:mod:`typing` library and
documented (*extensively*) using
`Numpy-style <https://numpydoc.readthedocs.io/en/latest/format.html>`_
docstrings.


Components
==========

The following full-featured components are provided which are ready to drop
into applications and use as-is:

.. toctree::
    :maxdepth: 1
    :glob:

    component.*


Foundations
===========

The following modules provide *mostly* full-featured components which require
*some degree* of subclassing and/or customization prior to using:

.. toctree::
    :maxdepth: 1
    :glob:

    foundation.*


Patterns
========

Abstract design pattern components to be tailored to specific use-cases are
provided for the following patterns:

.. toctree::
    :maxdepth: 1
    :glob:

    pattern.*


Utilities
=========

These commonly used (and often repeatedly re-written) utilities are provided:

.. toctree::
    :maxdepth: 1
    :glob:

    utility.*
