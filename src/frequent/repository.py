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
Repository base class for creating system-agnostic object storage.
"""
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Iterable
from typing import Optional
from typing import Type


class RepositoryException(Exception):
    """
    Exception class for repository-related errors.
    """
    pass


class ObjectNotFoundError(RepositoryException):
    """
    Exception thrown when an object could not be found.

    Parameters
    ----------
    id : object
        The identifier for which no object could be found.
    field : str
        The lookup field, which for the value `id`, no object could be
        found.

    """
    __obj_cls__: type = object

    def __init__(self, id: Any, field: str = 'id'):
        return super().__init__(
            f"No {self.__obj_cls__.__name__} found for: {field}={id}."
        )


class Repository(ABC):
    """
    Base class for creating object repositories.
    """
    __not_found_ex__: Type[ObjectNotFoundError] = ObjectNotFoundError

    @abstractmethod
    def add(self, obj: Any) -> None:
        """Adds an object to this storage repository.

        Parameters
        ----------
        obj : object
            The object to add to this storage repository.

        """
        pass

    @abstractmethod
    def all(self) -> Iterable[Any]:
        """All the objects stored in this repository.

        Returns
        -------
        :obj:`Iterable` of :obj:`object`
            An iterable object of all the objects contained in this
            repository.

        Note
        ----
        If you don't want your implementation to have the ability to
        return all of the objects simply have your implementation either
        return an empty container (e.g. `return []`) or (more
        pythonically) raise a :obj:`NotImplementedError`.

        """
        pass

    @abstractmethod
    def _get(self, id: Any) -> Optional[Any]:
        """Helper method to get the object with the given `id`.

        Parameters
        ----------
        id : object
            The identifier to use to get the associated object for.

        Returns
        -------
        :obj:`object` or :obj:`None`
            The object found for the given `id` (if found, otherwise
            :obj:`None`).

        """
        pass

    def get(self, id: Any) -> Any:
        """Gets an object from this storage repository.

        Parameters
        ----------
        id : object
            The identifier to use to get the associated object for.

        Returns
        -------
        object
            The object associated with the given `id`.

        Raises
        ------
        ObjectNotFoundError
            If no object was found for the given `id`.

        """
        obj = self._get(id)
        if obj is None:
            raise self.__not_found_ex__(id)
        return obj

    @abstractmethod
    def remove(self, id: Any) -> Any:
        """Removes and returns an object from this repository.

        Parameters
        ----------
        id : object
            The identifier to remove the associated object for.

        Returns
        -------
        object
            The object removed from this repository.

        Raises
        ------
        ObjectNotFoundError
            If no object was found for the given `id`.

        Note
        ----
        If you don't want your implementation to have the ability to
        remove objects simply have your implementation either return
        :obj:`None` or (more pythonically) raise a
        :obj:`NotImplementedError`.

        """
        pass
