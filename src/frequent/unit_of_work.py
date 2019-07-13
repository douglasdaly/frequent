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
Unit of Work pattern base classes for creating units of work.
"""
from abc import ABC
from abc import abstractmethod
from typing import Type


class UnitOfWork(ABC):
    """
    Base class for units of work.

    See Also
    --------
    UnitOfWorkManager

    """

    def __enter__(self) -> 'UnitOfWork':
        return self

    def __exit__(
        self,
        exc_type: Type[Exception],
        exc_value: Exception,
        traceback
    ) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        return

    @abstractmethod
    def commit(self) -> None:
        """Commits (persists) changes made during this unit of work."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rolls back any changes made during this unit of work."""
        pass


class UnitOfWorkManager(ABC):
    """
    Manager base class for creating :obj:`UnitOfWork` instances.

    See Also
    --------
    UnitOfWork

    """

    @abstractmethod
    def start(self) -> UnitOfWork:
        """Creates a new unit of work object to use.

        Returns
        -------
        UnitOfWork
            The new unit of work object to use.

        """
        pass
