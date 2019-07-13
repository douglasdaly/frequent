# -*- coding: utf-8 -*-
"""
Unit tests for the `messaging` module.
"""
from dataclasses import dataclass
from uuid import UUID

from frequent import messaging


@dataclass
class BasicMessage(messaging.Message):
    target: str
    code: int


@messaging.message
class DecoratedMessage:
    to: str
    sender: str
    text: str


class DecoratedHandler(messaging.MessageHandler):

    def handle(self, msg: DecoratedMessage) -> None:
        if msg.to == 'Liz':
            self.bus(DecoratedMessage(msg.sender, msg.to, 'Hi!'))
        return


class TestMessage(object):
    """
    Tests for the base :obj:`Message` object.
    """

    def test_create(self) -> None:
        msg = BasicMessage('calc_func', 42)
        assert isinstance(msg.id, UUID)
        assert msg.target == 'calc_func'
        assert msg.code == 42


def test_message_decorator() -> None:
    """Tests for the `@message` decorator."""
    msg = DecoratedMessage('Liz', 'Doug', 'Hello!')
    assert msg.to == 'Liz'
    assert msg.sender == 'Doug'
    assert msg.text == 'Hello!'
    assert isinstance(msg.id, UUID)
    return


def TestNoHandlersFoundException(object):
    """
    Tests for the :obj:`NoHandlersFoundException` class.
    """

    def test_exception(self) -> None:
        ex = messaging.NoHandlersFoundException(DecoratedMessage)
        assert str(ex) == \
            "No handlers found for message type 'DecoratedMessage'."
        return


class TestMessageBus(object):
    """
    Tests for the :obj:`MessageBus` class.
    """

    def test_create(self) -> None:
        t_bus = messaging.MessageBus()
        assert repr(t_bus) == "<MessageBus registry=0>"

        t_msg = DecoratedMessage('Liz', 'Doug', 'Hi!')
        try:
            t_bus.handle(t_msg)
            assert False
        except messaging.NoHandlersFoundException:
            assert True
        try:
            t_bus(t_msg)
            assert False
        except messaging.NoHandlersFoundException:
            assert True
        return


class TestHandlerRegistry(object):
    """
    Tests for the :obj:`HandlerRegistry` class.
    """

    def test_create(self) -> None:
        registry = messaging.HandlerRegistry()
        assert len(registry) == 0
        assert repr(registry) == "<HandlerRegistry mappings={}>"
        return

    def test_usage(self) -> None:
        registry = messaging.HandlerRegistry()

        t_bus = messaging.MessageBus()
        t_handler_a = DecoratedHandler(t_bus)

        registry.add(DecoratedMessage, t_handler_a)
        assert len(registry) == 1
        assert registry.get(DecoratedMessage) == [t_handler_a]
        assert registry.get(BasicMessage) is None
        assert repr(registry) == (
            "<HandlerRegistry mappings={"
            "\n   'DecoratedMessage': [1 handler],"
            "\n }\n>"
        )

        thl = registry.remove(DecoratedMessage)
        assert len(thl) == 1
        assert len(registry) == 0
        assert thl[0] == t_handler_a

        o_bus = messaging.MessageBus()
        t_handler_b = DecoratedHandler(o_bus)
        registry.add(DecoratedMessage, t_handler_b, t_handler_a)
        assert len(registry) == 1
        assert len(registry[DecoratedMessage]) == 2
        assert registry.get(DecoratedMessage) == [t_handler_b, t_handler_a]
        assert repr(registry) == (
            "<HandlerRegistry mappings={"
            "\n   'DecoratedMessage': [2 handlers],"
            "\n }\n>"
        )

        registry.clear()
        assert len(registry) == 0
        try:
            _ = registry[DecoratedMessage]
            assert False
        except messaging.NoHandlersFoundException:
            assert True
        return
