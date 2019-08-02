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
Messaging framework foundations.
"""
from abc import ABC
from abc import ABCMeta
from abc import abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union
from uuid import UUID
from uuid import uuid1


T_Handler = Union[Callable[['Message'], None], 'MessageHandler']


class Message(ABC):
    """
    Base class for all message objects.

    Attributes
    ----------
    id : UUID
        A unique universal identifier for this message.

    Example
    -------
    Derived message classes can be created from this class, though the
    :obj:`message` decorator is simpler to use.  To create a message
    class directly from this base class:

    .. code-block :: python

        from dataclasses import dataclass

        @dataclass
        class DirectMessage(Message):
            to: str
            sender: str
            text: str

    >>> msg = DirectMessage('Liz', 'Doug', 'Hello!')
    >>> msg
    DirectMessage(to='Liz', sender='Doug', text='Hello!')
    >>> msg.id
    UUID('5a47c192-a50b-11e9-bc30-a434d9ba8632')

    See Also
    --------
    convert_to_message, message

    """
    id: UUID = uuid1()


def convert_to_message(cls: type, target_cls: Type[Message]) -> Type[Message]:
    """Converts the given `cls` to the specified :obj:`Message` class.

    User's should prefer to use the :obj:`message` decorator as it's
    easier to use and acts purely as a pass-through to this function.
    This function is provided to allow users to create
    decorators/functions to convert classes to their own custom
    :obj:`Message` subclasses.

    Parameters
    ----------
    cls : type
        The class to convert to a :obj:`Message` subclass.
    target_cls : :obj:`type` of :obj:`Message`
        The :obj:`Message` (sub)class to convert the given `cls` to.

    Returns
    -------
    :obj:`type` of :obj:`Message`
        The new class, converted to a subclass of :obj:`Message`.

    See Also
    --------
    message, Message

    """
    new_cls = dataclass(cls, frozen=True)
    if not isinstance(cls, target_cls):
        new_cls = type(cls.__name__, (new_cls, target_cls), {})
    return new_cls


def message(cls: type) -> Type[Message]:
    """Decorator for easily creating new :obj:`Message` sub-classes.

    Parameters
    ----------
    cls : type
        The class to convert to a :obj:`Message` subclass.

    Returns
    -------
    :obj:`type` of :obj:`Message`
        The new class, converted to a subclass of :obj:`Message`.

    Example
    -------
    To create a new :obj:`Message` class using this decorator:

    .. code-block:: python

        @message
        class MyMessage:
            target: str
            value: int

    Then new instances are created just like named tuples:

    >>> msg = MyMessage('calc_func', 42)
    >>> msg
    <MyMessage target='calc_func' value=42>

    See Also
    --------
    convert_to_message, Message

    """
    return convert_to_message(cls, Message)


class MessageHandler(object, metaclass=ABCMeta):
    """
    Message handling base class.
    """

    def __init__(self, bus: 'MessageBus'):
        self._bus = bus
        return super().__init__()

    @property
    def bus(self) -> 'MessageBus':
        """MessageBus: The message bus to use for subsequent messages.
        """
        return self._bus

    def __call__(
        self,
        msg: Message,
        successor: Optional[T_Handler] = None
    ) -> None:
        return self.handle(msg, successor=successor)

    @abstractmethod
    def handle(
        self,
        msg: Message,
        successor: Optional[T_Handler] = None
    ) -> None:
        """Handles the given message object.

        Parameters
        ----------
        msg : Message
            The message object to handle.
        successor : :obj:`MessageHandler` or :obj:`Callable`, optional
            The next handler in the chain.

        """
        pass


class HandlerRegistry(Mapping):
    """
    A registry containing mappings of message type to handler(s).

    Examples
    --------
    To add mappings:

    >>> registry = HandlerRegistry()
    >>> msg_bus = MessageBus()
    >>> my_handler = MyMessageHandler(msg_bus)
    >>> registry.add(MyMessage, my_handler)
    >>> registry
    <HandlerRegistry mappings={
       'MyMessage': [1 handler],
    }>

    """

    def __init__(self) -> None:
        self._store = {}
        return super().__init__()

    def __repr__(self) -> str:
        ret = f"<{self.__class__.__name__} mappings={{"
        if not self._store:
            return ret + "}>"
        for k, v in self._store.items():
            ret += f"\n   '{k.__name__}': [{len(v)} handler"
            if len(v) > 1:
                ret += 's'
            ret += "],"
        return ret + "\n}>"

    def __getitem__(self, key: Type[Message]) -> Sequence[T_Handler]:
        ret = self._store.get(key)
        if not ret:
            raise NoHandlersFoundException(key)
        return ret

    def __iter__(self) -> Iterator:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def add(
        self,
        msg_cls: Type[Message],
        handler: T_Handler,
        *handlers: Tuple[T_Handler, ...]
    ) -> None:
        """Adds message handler(s) for the specified message type.

        Parameters
        ----------
        msg_cls : :obj:`type` of :obj:`Message`
            The message class to add handler mappings for.
        handler : :obj:`MessageHandler` or :obj:`Callable`
            The message handler to map to the given ``msg_cls`` type.
        handlers : optional
            Additional message handler(s) to map to the given
            ``msg_cls`` type.

        """
        if msg_cls not in self._store:
            self._store[msg_cls] = []
        self._store[msg_cls].extend((handler,) + handlers)
        return

    def clear(self) -> None:
        """Clears all the registered message handler mappings."""
        return self._store.clear()

    def get(
        self,
        key: Type[Message],
        default: Any = None
    ) -> Sequence[T_Handler]:
        """Gets the message handler(s) associated with the given type.

        Parameters
        ----------
        key : :obj:`type` of :obj:`Message`
            The message type to get the associated handlers for.
        default : optional
            The value to return if no associated handlers are found.

        Returns
        -------
        :obj:`Sequence` of :obj:`Callable` or :obj:`object`
            The message handlers found (if any) or the ``default`` value
            given if no message handlers are found.

        """
        try:
            return self[key]
        except NoHandlersFoundException:
            return default

    def remove(self, msg_cls: Type[Message]) -> Sequence[T_Handler]:
        """Removes all mappings for the specified message type.

        Parameters
        ----------
        msg_cls : :obj:`type` of :obj:`Message`
            The message type to remove all handler mappings for.

        Returns
        -------
        :obj:`Sequence` of :obj:`Callable`
            The message handlers which were mapped to the specified
            ``msg_cls`` type.

        Raises
        ------
        NoHandlersFoundException
            If no handlers were mapped to the specified ``msg_cls``
            type.

        """
        handlers = self._store.pop(msg_cls)
        if handlers is None:
            raise NoHandlersFoundException(msg_cls)
        return handlers


class MessageBus(object):
    """
    Message bus for routing messages to the appropriate handlers.

    Parameters
    ----------
    registry : HandlerRegistry, optional
        The initial message type to handler mapping registry to use.

    """
    __registry_cls__: Type[HandlerRegistry] = HandlerRegistry

    def __init__(self, registry: Optional[HandlerRegistry] = None) -> None:
        self._registry = registry or self.__registry_cls__()
        return super().__init__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} registry={len(self.registry)}>"

    @property
    def registry(self) -> HandlerRegistry:
        """HandlerRegistry: The handler mapping registry in use."""
        return self._registry

    def __call__(self, msg: Message) -> None:
        return self.handle(msg)

    def handle(self, msg: Message) -> None:
        """Handles the given message.

        Parameters
        ----------
        msg : Message
            The message object to handle.

        Raises
        ------
        NoHandlersFoundException
            This exception will be raised if no message handlers were
            registered for the given type of message.

        """
        for handler in self.registry[type(msg)]:
            handler.handle(msg)
        return


def chain(*handlers: Tuple[T_Handler, ...]) -> T_Handler:
    """Chains multiple handlers together.

    Parameters
    ----------
    handlers : :obj:`MessageHandler` or :obj:`Callable`
        The handlers to chain together, with each being passed the next
        handler via the ``successor`` keyword-argument.

    Returns
    -------
    Callable
        The chained callable to use for message handling.

    Examples
    --------
    To chain together two handlers into one:

    >>> class MessageIdLogger(MessageHandler):
    ...     def handle(self, msg, successor=None):
    ...         # Print our message's ID
    ...         print(msg.id)
    ...         # ... then call the next handler.
    ...         return successor(msg)
    ...
    >>> def my_next_handler(msg):
    ...     if msg.code == 42:
    ...         print('The answer!')
    ...     else:
    ...         print('Not the answer...')
    ...     return
    >>> chained_handler = chain(MessageIdLogger(), my_next_handler)
    >>> ans_msg = MyMessage(42)
    >>> not_ans_msg = MyMessage(41)
    >>> chained_handler(answer_msg)
    5a47c192-a50b-11e9-bc30-a434d9ba8632
    The answer!
    >>> chained_handler(not_ans_msg)
    9a47c651-a52b-11f9-bc80-a484d9ba8633
    Not the answer

    """
    def _chain(head, tail):
        if not tail:
            return head
        nxt_head, *nxt_tail = tail
        return partial(head, successor=_chain(nxt_head, nxt_tail))

    head, *tail = handlers
    return _chain(head, tail)


class MessagingException(Exception):
    """
    Messaging framework base exception.
    """
    pass


class NoHandlersFoundException(MessagingException):
    """
    Exception thrown if no message handlers were found.

    Parameters
    ----------
    msg_cls : :obj:`type` of :obj:`Message`
        The message type which caused this exception to be thrown.

    """

    def __init__(self, msg_cls: Type[Message]):
        return super().__init__(
            f"No handlers found for message type '{msg_cls.__name__}."
        )
