###################
Messaging Framework
###################

The :doc:`frequent.messaging <../api/frequent.messaging>` module provides a
skeleton for implementing your own messaging framework.  Useful for
applications which implement the :doc:`pattern.repository` and/or the
:doc:`pattern.unit_of_work` patterns as a command/command-handler system.  The
advantages of using this kind of system are:

- It **decouples** :obj:`Message` objects from the business-logic which handles
  them (:obj:`MessageHandler` or any :obj:`Callable` taking a message object as
  its first argument).
- It allows **chaining** of handlers together in order to call subsequent
  handlers on a message in a sequential way via a simple :obj:`chain` function.
- It allows **broadcasting** a single message to multiple handlers (different
  from sequential chaining).
- It uses a **centralized** :obj:`MessageBus` to shuttle messages about (you
  *may* want to create your own instance with the :doc:`utility.singleton`
  module to make it a singleton object).
- Each :obj:`MessageHandler` has a handle to a :obj:`MessageBus` instance it
  can use to send any subsequent messages (potentially to different buses than
  the bus which transmitted the original message to the handler).


Usage
=====

The :obj:`frequent.messaging` module provides all the pieces needed to create
custom :obj:`Message <frequent.messaging.Message>` and
:obj:`MessageHandler <frequent.messaging.MessageHandler>` classes as well as
the components needed to facilitate message passing via the
:obj:`MessageBus <frequent.messaging.MessageBus>`.  In the examples below
we'll create a *very basic* messaging framework to deliver messages to the
appropriate user's mailbox to show some of these features.


Creating Message Classes
------------------------

To start you'll need to create your own ``Message`` classes, which can be done
using the ``@message`` decorator:

.. code-block:: python

    from frequent.messaging import message

    @message
    class MyMessage:
        sender: str
        recipient: str
        text: str


The decorator will automatically add the ``Message`` class to the base
classes (``__bases__``) of the ``MyMessage`` class and cast the class as a
`dataclass <https://docs.python.org/3/library/dataclasses.html>`_ via the new
(as of Python 3.7) standard library.

.. note::

    Each instance of ``Message`` has an auto-generated ``id`` attribute (a
    :obj:`UUID`) generated using ``uuid.uuid1()`` from the standard library.


Creating Message Handlers
-------------------------

Now let's create a message handler for sending messages by subclassing the
:obj:`MessageHandler` abstract base class:

.. code-block:: python

    from frequent.messaging import MessageHandler

    class MyMessageHandler(MessageHandler):

        def __init__(self, bus, mailboxes):
            self._mailboxes = mailboxes
            return super().__init__(bus)

        def handle(self, msg, successor=None):
            self._mailboxes[msg.recipient].append(msg)
            return

We can create the instance now with:

>>> bus = MessageBus()
>>> mailboxes = []
>>> my_message_handler = MyMessageHandler(bus, mailboxes)

.. note::

    Handlers can also be functions which take the first argument as the message
    object and an (optional) keyword-argument ``successor`` for the next
    handler to call (if chaining handlers together).  The advantage of the
    :obj:`MessageHandler` object is it's reference to a :obj:`MessageBus` which
    it can use to transmit additional messages (if needed).


Chaining Handlers Together
--------------------------

Suppose we want to first log a message prior to handling it, we can create a
function to do that which will then call the next function in the chain:

.. code-block:: python

    from frequent.messaging import chain

    def log_message_handler(msg, successor):
        print(f"{msg.sender}->{msg.recipient}: '{msg.text}'")
        return successor(msg)

Now we chain this one together with the previous ``MyMessageHandler``:

>>> chained_handler = chain(log_message_handler, my_message_handler)
>>> chained_handler(MyMessage('Doug', 'Liz', 'Hello!'))
Doug->Liz: 'Hello!'


Configuring the MessageBus
--------------------------

We can now create and configure the :obj:`MessageBus` and send messages to the
appropriate handler(s).  First let's setup a helper object to store messages a
user has received (the ``mailboxes`` object - a simple :obj:`dict` which stores
:obj:`list`s of ``MyMessage`` objects using the message recipient's name as the
key).

>>> mailboxes = defaultdict(list)

Then we can create the :obj:`MessageBus` and the ``MyMessageHandler``
and lastly, map the ``MyMessage`` :obj:`Message` type to it in the
:obj:`MessageBus`'s registry (an instance of :obj:`HandlerRegistry`):

>>> msg_bus = MessageBus()
>>> msg_handler = SendMessageHandler(message_bus, mailboxes)
>>> message_bus.registry.add(MyMessage, mymsg_handler)


Using the New Framework
-----------------------

Now that the ``MyMessage`` class is mapped to our instance of the
``MyMessageHandler`` we can pass messages to the ``msg_bus`` instance to have
them stored in the appropriate user's mailbox (via the ``msg_handler``):

>>> msg_a = MyMessage('Doug', 'Liz', 'How are you?')
>>> msg_bus(msg_a)
>>> rcvd = mailboxes['Liz'].pop()
>>> rcvd
MyMessage(sender='Doug', recipient='Liz', text='How are you?')
>>> msg_b = MyMessage(rcvd.recipient, rcvd.sender, "I'm great, how are you?")
>>> msg_bus(msg_b)
>>> mailboxes['Doug'].pop()
MyMessage(sender='Liz', recipient='Doug', text='I'm great, how are you?')


Links
=====

API
---

Module
    :doc:`frequent.messaging <../api/frequent.messaging>`

Decorators
    :obj:`message <frequent.messaging.message>`

Functions
    :obj:`chain <frequent.messaging.chain>`

Abstract Classes
    :obj:`Message <frequent.messaging.Message>`,
    :obj:`MessageHandler <frequent.messaging.MessageHandler>`

Classes
    :obj:`HandlerRegistry <frequent.messaging.HandlerRegistry>`,
    :obj:`MessageBus <frequent.messaging.MessageBus>`

Exceptions
    :obj:`MessagingException <frequent.messaging.MessagingException>`,
    :obj:`NoHandlersFoundException <frequent.messaging.NoHandlersFoundException>`

Type Hints
    :obj:`T_Handler <frequent.messaging.T_Handler>`
