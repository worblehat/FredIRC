Beginner's Guide
================

**Prerequisites**: :doc:`install`

This page will guide you through the steps to implement a first IRC bot with
FredIRC. It will be able to connect to a channel, greet new users and
respond to them. The complete source code of this example can be found at the
end of this page.

Note that we won't go very much into details here. For a complete
explanation of the used classes and methods see the :doc:`api`.

IRCHandler
----------

In FredIRC a bot is a class that handles events from an IRC server and may
respond to them in some way. The base class for all bots is therefore
:py:class:`IRCHandler<fredirc.IRCHandler>`, which defines different
handler-methods that are called on specific
events (e.g.
:py:meth:`handle_channel_message()<fredirc.IRCHandler.handle_channel_message()>`
, :py:meth:`handle_join()<fredirc.IRCHandler.handle_join()>`,...).
In :py:class:`IRCHandler<fredirc.IRCHandler>` all these methods are empty,
so by default it does not do anything.

:py:class:`BaseIRCHandler<fredirc.BaseIRCHandler>` is a subclass of
:py:class:`IRCHandler<fredirc.IRCHandler>` and implements the absolute minimum
to get a bot running. It is up to you, to subclass
:py:class:`BaseIRCHandler<fredirc.BaseIRCHandler>` and implement the
handler-methods you need.

So first you'll create a class for the bot:

.. code-block:: python

    from fredirc import BaseIRCHandler

    class MyBot(BaseIRCHandler):
        pass

Connect to a Server
-------------------

To connect your bot to an IRC server, you have to create an instance of
:py:class:`IRCClient<fredirc.IRCClient>` and pass your bot object to its
constructor:

.. code-block:: python

    from fredirc import IRCClient

    client = IRCClient(MyBot(), "Fred", "irc.freenode.com")
    client.run()

The other two arguments are the bot's nick name and the IRC server address.
Calling :py:meth:`run()<fredirc.IRCClient.run()>` on the client will start it.
:py:meth:`run()<fredirc.IRCClient.run()>` will not return as
long as the client is running and connected to the server. So the actual
event loop that coordinates the communication with the server is implemented
inside of it.

Join a Channel
---------------

So far your bot will just connect to the server *irc.freenode.com* and register
with nick *Fred*.

Afterwards you probably want the bot to join a channel. To do so, implement
the :py:meth:`handle_register()<fredirc.IRCHandler.handle_register()>` method
of :py:class:`IRCHandler<fredirc.IRCHandler>`:

.. code-block:: python

    class MyBot(BaseIRCHandler):

        def handle_register(self):
            self.client.join("#SomeChannel")

This method will be called after successful registration. A bot has a client
member that is the :py:class:`IRCClient<fredirc.IRCClient>` instance it is
running in. To join a channel you can use the proper method of the client.
Actually all communication with the server is done via method calls on
``self.client``.

Communicate with the Channel
----------------------------

Now that your bot is in a channel, it can communicate with other users in that
channel. For example it could greet new users. To do so, use
:py:meth:`handle_join()<fredirc.IRCHandler.handle_join()>`
which is called whenever a user joins the channel:


.. code-block:: python

    class MyBot(BaseIRCHandler):

        (...)

        def handle_join(self, channel, nick):
            self.client.send_message(channel, 'Welcome, ' + nick + '!')

Of course your bot can also reply to messages from other users.
As an example, you can use
:py:meth:`handle_channel_message()<fredirc.IRCHandler.handle_channel_message()>`
to respond to someone who sends 'Hello Fred' to the channel:

.. code-block:: python

    class MyBot(BaseIRCHandler):

        (...)

        def handle_channel_message(self, channel, message, sender):
            if messsage.strip() == "Hello " + self.client.nick:
                self.client.send_message("Hi " + sender + ". How are you?")

.. _guide_handle-errors:

Handle Errors
-------------

In an IRC session a lot of unexpected situations or even errors can occur.
The server reports those errors by sending an error reply to the client.
To react to those errors appropriately you might want to implement
:py:meth:`handle_error()<fredirc.IRCHandler.handle_error()>`.

A common 'error' that should be handled is the situation where your chosen nick
name is already in use by someone else. In that case you should register
with a different nick. Here we just append a random number to the
previous nick:

.. code-block:: python

    from fredirc import Err
    from random import Random

    class MyBot(BaseIRCHandler):

        (...)

        def handle_error(self, num, **params):
            if num == Err.NICKNAMEINUSE:
                new_nick = params['nick'] + Random().randint(1, 9)
                self.client.register(nick = new_nick)

The parameter ``num`` contains a number that can be used to identify the error
and ``params`` is a variable length list of named values specific to the error.
In case of ``NICKNAMEINUSE`` error, ``params['nick']`` contains the nick you
tried to register with.

See :py:class:`Err<fredirc.Err>` for a complete list of errors and their
parameters.

Run the Bot
---------------

Assuming you've put your code in a file called ``bot.py``, you can run your bot
with:

.. code-block:: bash 

    $ python3 bot.py

By default a log file called ``irc.log`` will be created in the current working
directory. So if your bot does not behave as expected you should take a look
at this file. You can also change the
:py:meth:`log level<fredirc.IRCClient.set_log_level()>` or
:py:meth:`disable logging<fredirc.IRCClient.enable_logging()>`
via the :py:class:`IRCClient<fredirc.IRCClient>` instance.

If you want to run the client in the background without occupying a terminal
I recommend the ``nohup`` command on Linux:

.. code-block:: bash

    $ nohup python3 bot.py &

Complete Example
----------------

The complete code from above in one listing:

.. code-block:: python

    from fredirc import BaseIRCHandler
    from fredirc import Err
    from fredirc import IRCClient

    from random import Random

    client = IRCClient(MyBot(), "Fred", "irc.freenode.com")
    client.run()

    class MyBot(BaseIRCHandler):

        def handle_register(self):
            self.client.join("#SomeChannel")

        def handle_join(self, channel, nick):
            self.client.send_message(channel, 'Welcome, ' + nick + '!')

        def handle_channel_message(self, channel, message, sender):
            if messsage.strip() == "Hello " + self.client.nick:
                self.client.send_message("Hi " + sender + ". How are you?")

        def handle_error(self, num, **params):
            if num == Err.NICKNAMEINUSE:
                new_nick = params['nick'] + Random().randint(1, 9)
                self.client.register(nick = new_nick)

