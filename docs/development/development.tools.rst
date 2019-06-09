#################
Development Tools
#################

This project has some tools included with it to make development and
testing easier.

.env File
=========

This file is not committed to source control, but a ``sample.env`` is.
It's used to specify local, machine-specific environment variables to
use.  It's not *strictly* necessary for getting up-and-running for
development, but it specifies three important variables used by the
Makefile:

:PKG_MGR: The Python package manager to use (``pip`` or ``pipenv``).
:PYTHON: The Python interpreter to use (``python`` or ``python3``).
:TODO_CMD: The command you use to call the ``todo.sh``.
:PYTEST_CORES: The number of processors to use for ``pytest`` (the
    default is ``auto``).


Makefile
========

The majority of the tasks related to development are handled via
Makefile commands.  First, make sure you've got ``make`` installed on
your system (included on Linux by default), for more information on
``make`` see
`the GNU Make homepage <https://www.gnu.org/software/make/>`_.

To see a listing of all the commands included in the project's Makefile
simply type:

.. code-block:: bash

    $ make

Which will run the default target, which is ``make help``, which
displays all of the commands included in the Makefile as well as a short
description of each:

.. literalinclude:: makefile_help.txt
    :encoding: utf-8
    :language: text


Git
===

Git is used for all of the source code control, the project also uses Git
Flow for the general development approach, for details on git flow see
`the branching model <https://nvie.com/posts/a-successful-git-branching-model/>`_
as well as
`this great cheat-sheet <https://danielkummer.github.io/git-flow-cheatsheet/>`_.

The general gist is that you develop new features on (aptly-named)
``feature`` branches, which get merged into the main ``development``
branch.  When ready for a release the ``development`` branch is branched
off into a new (and generally temporary) ``release`` branch.  The
finishing touches are done there and then the ``release`` branch is
merged into the ``master`` branch and back into the ``development``
branch, the ``master`` branch is tagged and released.  There is also a
``hotfix`` branch for when changes need to be made to both the
``master`` and ``development`` branches to correct a pressing issue.


Changelogs
==========

All changes to this project are maintained in the project's primary
``CHANGELOG.md`` file, as well as individual reStructuredText files in
the project documentation for each minor version release.  More information
can be found :doc:`in that section <changelogs/changelogs>`.


todo-txt
========

There's a directory titled ``todo`` in the main project folder, as well
as a ``.envrc`` file.  These work together with
`the todo-txt cli <https://github.com/todotxt/todo.txt-cli>`_ to manage
the project's todo lists.  The data is stored in the ``txt`` files in
the ``todo`` directory, and the ``.envrc`` defines an environment
variable ``TODO_DIR`` which points to that directory (instead of the
user's default directory) for all the todos.  You can learn more about
the todo-txt program from
`that project's USAGE file <https://github.com/todotxt/todo.txt-cli/blob/master/USAGE.md>`_
or the tools ``help`` (via ``todo help`` or ``t help``).

.. warning::

    The ``todo.sh`` script only works on Linux and Mac operating systems
    (by default).  If you're on Windows you may be able to configure
    the ``.env`` file's ``TODO_CMD`` to work on your system but if not
    you can easily add/complete todo item's via the .txt files in the
    ``todos`` directory with your text editor of choice.


For this project's todo's the ``+project`` tag is used for specifying
the ``CHANGELOG`` category.  For the todos we use the present tense when
specifying this (where applicable, e.g. ``add`` in the todos corresponds
to the ``added`` section in the changelogs).  If none is given the tools
will assume ``misc``.  The options are:

- ``add``
- ``change``
- ``deprecate``
- ``remove``
- ``fix``
- ``security``
- ``misc``

The ``@context`` tag is optional and can be used to specify the specific
issue number that the todo is in reference to.

**Examples**

Add a todo to refactor a class named "Model":

.. code-block:: bash

    $ t a "Refactor Model to extract file functions +change"

Add a todo to fix a bug from issue #1234:

.. code-block:: bash

    $ t a "Fix bug in Parameter for arrays +fix @1234"

These todo files are used by the project's invoke tasks/Makefile
commands to auto-populate changelogs and such.  The todos can also be
prioritized using an A-Z system (A being the highest, Z the lowest) via
the todo-txt tool's (``p`` or ``pri`` command).  For instance, if we
wanted to set the priority for todo #2 to ``B``:

.. code-block:: bash

    $ t pri 2 B

