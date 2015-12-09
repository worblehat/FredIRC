API Reference
=============

This is the documentation of the API for users of FredIRC.

Overview
---------

The following classes are the main part of the API and might be of
interest to anyone who uses FredIRC:

* :py:class:`.IRCHandler` - Abstract base class containing event handler
  methods that can be implemented in subclasses.
* :py:class:`.BaseIRCHandler` - You probably want to subclass this, to
  overwrite handler methods in your bot. It is derived from IRCHandler itself.
* :py:class:`.IRCClient` - Implements basic IRC client functionality and runs
  the whole framework. Provides an interface to send messages to the server.
* :py:class:`.Task` - Schedule tasks to be executed by the event loop at a
  specific time.


``IRCHandler`` Class
--------------------

.. autoclass:: fredirc.IRCHandler
    :members:
    :undoc-members:

``BaseIRCHandler`` Class
------------------------

.. autoclass:: fredirc.BaseIRCHandler

``IRCClient`` Class
-------------------

.. autoclass:: fredirc.IRCClient
    :members:
    :undoc-members:
    :exclude-members: __call__, connect_lost, connection_made,
        data_received, eof_received
.. no idea why we have to exclude __call__ although :special-members:
   is not specified

``ChannelInfo`` Class
---------------------
.. autoclass:: fredirc.ChannelInfo
    :members:
    :undoc-members:

``Task`` Class
--------------

.. autoclass:: fredirc.Task
    :members:
    :undoc-members:

``Err`` Class
-------------

.. autoclass:: fredirc.Err
    :members:
    :undoc-members:

Exception Classes
-----------------

.. autoclass:: fredirc.FredIRCError
    :members:
    :undoc-members:

.. autoclass:: fredirc.MessageHandlingError
    :members:
    :undoc-members:

.. autoclass:: fredirc.ParserError
    :members:
    :undoc-members:

.. autoclass:: fredirc.ConnectionTimeoutError
    :members:
    :undoc-members:

