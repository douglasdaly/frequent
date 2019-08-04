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
Unit tests for the messaging module.
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
        return

    def test_usage(self) -> None:
        registry = messaging.HandlerRegistry()

        t_bus = messaging.MessageBus()
        t_handler_a = DecoratedHandler(t_bus)

        registry.add(DecoratedMessage, t_handler_a)
        assert len(registry) == 1
        assert registry.get(DecoratedMessage) == [t_handler_a]
        assert registry.get(BasicMessage) is None

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

        registry.clear()
        assert len(registry) == 0
        try:
            _ = registry[DecoratedMessage]
            assert False
        except messaging.NoHandlersFoundException:
            assert True
        return


def test_chain():
    """Tests the :obj:`messaging.chain` method."""
    msg_q = BasicMessage('DeepThought', -1)
    msg_a = BasicMessage('The Mice', 42)

    log_ids = []
    log_res = []

    class LogMsgHandler(messaging.MessageHandler):
        def handle(
            self, msg: BasicMessage, successor: messaging.T_Handler = None
        ) -> None:
            log_ids.append(msg.id)
            if successor:
                successor(msg)
            return

    def save_result(msg: BasicMessage) -> None:
        log_res.append(f"{msg.target}: {msg.code}")
        if msg.code == 42:
            log_res.append("You're welcome.")
        return

    bus = messaging.MessageBus()
    log_handler = LogMsgHandler(bus)

    chained = messaging.chain(log_handler, save_result)
    chained(msg_q)
    chained(msg_a)

    assert len(log_ids) == 2
    assert log_ids[0] == msg_q.id
    assert log_ids[1] == msg_a.id

    assert len(log_res) == 3
    assert log_res[0] == f"{msg_q.target}: {msg_q.code}"
    assert log_res[1] == f"{msg_a.target}: {msg_a.code}"
    assert log_res[2] == "You're welcome."

    log_ids.clear()
    log_res.clear()

    def check_target(
        msg: BasicMessage, successor: messaging.T_Handler
    ) -> None:
        if msg.target == 'The Mice':
            return successor(msg)
        return

    chained_two = messaging.chain(log_handler, check_target, save_result)
    chained_two(msg_q)
    chained_two(msg_a)

    assert len(log_ids) == 2
    assert log_ids[0] == msg_q.id
    assert log_ids[1] == msg_a.id

    assert len(log_res) == 2
    assert log_res[0] == f"{msg_a.target}: {msg_a.code}"
    assert log_res[1] == "You're welcome."

    chained_break = messaging.chain(save_result, check_target)
    try:
        chained_break(msg_a)
        assert False
    except TypeError:
        assert True

    return
