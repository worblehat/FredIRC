# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
Classes related to the basic IRC-client implementation of FredIRC.
"""

__all__ = ['IRCClient']

import asyncio
import codecs
import logging
import time

from fredirc import messages
from fredirc.errors import ConnectionTimeoutError
from fredirc.messages import ChannelMode
from fredirc.parsing import ChannelModeChange
from fredirc.processor import MessageProcessor


class IRCClient(asyncio.Protocol):
    """ IRC client class managing the network connection and dispatching
        messages from the server.

    .. warning:: Currently only a single IRCClient instance is allowed! Don't
        run multiple clients. This will result in undefined behaviour. This
        will probably be fixed in future releases.

    To connect to the server and start the processing event loop call
    :py:meth:`run()<.IRCClient.run>` on your IRCClient instance.
    Nick, user name, real name and password are used by
    :py:meth:`.register` to register the client to the server.

    Args:
        handler (:py:class:`IRCHandler<fredirc.IRCHandler>`): \
            handler that handles events from this client
        nick (str): nick name for the client
        server (str): server name or ip
        port (int): port number to connect to
        user_name (str): User name for registration to the server.
                         If None, nick is used.
        real_name (str): Full name of the client. If None, nick is used.
        password (str): Optional password that can be used to
                        authenticate to the server.
    """

    def __init__(self,
                 handler,
                 nick,
                 server,
                 port=6667,
                 user_name=None,
                 real_name=None,
                 password=None):
        asyncio.Protocol.__init__(self)
        self._handler = handler
        self._state = IRCClientState()
        self._buffer = []
        # Variable to determine if we want to reconnect the transport and
        # re-run the event loop automatically after it was stopped:
        self._reconnect = False
        # Register customized decoding error handler
        codecs.register_error('log_and_replace', self._decoding_error_handler)
        # Configure logger
        self._logger = logging.getLogger('FredIRC')
        log_file_handler = logging.FileHandler('irc.log')
        log_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(name)s (%(levelname)s): %(message)s'))
        self._logger.addHandler(log_file_handler)
        self._logger.setLevel(logging.INFO)
        self.enable_logging(True)
        self._logger.info('Initializing IRC client')
        # Init message processor
        self._processor = MessageProcessor(self._handler, self._state,
                                           self._logger)
        # Connection and registration info
        self._configured_nick = nick
        self._configured_server = server
        self._configured_port = port
        self._configured_user_name = user_name if user_name else nick
        self._configured_real_name = real_name if real_name else nick
        self._configured_password = password
        # Pass this client object to the handler
        self._handler.handle_client_init(self)

    def run(self):
        """ Start the client's event loop.

        An endless event loop which will call the ``handle_*`` methods from
        :py:class:`.IRCHandler`. The client connects to the server
        and calls :py:meth:`handle_connect()<.IRCHandler.handle_connect>` on
        its handler if this is successful.
        If the connection is closed the client can re-establish it without exiting the
        event loop via :py:meth:`reconnect()<.reconnect>`.
        To terminate the event loop use :py:meth:`terminate()<.terminate>`.
        Afterwards run() will return.
        """
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            try:
                while True:
                    self._reconnect = False
                    self._connect()
                    loop.run_forever()
                    if not self._reconnect:
                        break
            finally:
                loop.close()

    def reconnect(self, delay=0.0):
        """ Reconnect the client to the server.

        This only reconnects a disconnected client. If the client is still
        connected to the server, it will have no effects.
        So reconnect() could be used to re-establish the connection on
        :py:meth:`handle_disconnect()<.IRCHandler.handle_disconnect>`.

        After successful reconnection
        :py:meth:`handle_connect()<.IRCHandler.handle_connect>` gets called.

        Args:
            delay (float): Time to delay the reconnection attempt in seconds.
                           Can be useful as servers might refuse a client
                           that reconnects to fast.
        """
        if self._state.connected:
            return
        self._reconnect = True
        time.sleep(delay)
        asyncio.get_event_loop().stop()

    def enable_logging(self, enable):
        """ Enable or disable logging.

        Logging is enabled by default.

       Args:
            enable (bool): ``True`` to enable logging, ``False`` disable it
        """
        if enable:
            self._logger.removeFilter(lambda x: 0)
        else:
            self._logger.addFilter(lambda x: 0)

    def set_log_level(self, level):
        """ Set the log level that is used if logging is enabled.

        Args:
            level (int): the log level as defined by constants in Python's \
            `logging module <https://docs.python.org/2/library/logging.html#logging-levels>`_ \
            (``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``)
        """
        self._logger.setLevel(level)

    def terminate(self):
        """ Shutdown the IRCClient by terminating the event loop.

        Control flow will continue after the call to :py:meth:`.IRCClient.run`.
        """
        self._logger.info('Event-Loop terminated.')
        self._reconnect = False
        asyncio.get_event_loop().stop()

    # --- IRC related methods ---

    def register(self, nick=None, user_name=None, real_name=None, password=None):
        """ Register to the IRC server.

        When called with no arguments, registration data given on initialization
        or the last call to register is used.

        Args:
            nick (str): Nick name for the client.
            user_name (str): User name for registration to the server.
            real_name (str): Full name of the client.
            password (str): Optional password that might be used to
                            authenticate to the server.
        """
        # Configure registration data
        if nick:
            self._configured_nick = nick
        if user_name:
            self._configured_user_name = user_name
        if real_name:
            self._configured_real_name = real_name
        if password:
            self._configured_password = password
        # Send registration messages
        if self._configured_password:
            self._send_message(messages.password(self._configured_password))
        self._send_message(messages.nick(self._configured_nick))
        self._send_message(messages.user(
            self._configured_user_name, self._configured_real_name))

    def join(self, channel, *channels):
        """ Join the specified channel(s).

        Note that no matter what case the channel strings are in, in the
        handler functions of :py:class:`.IRCHandler` channel names will
        probably always be lower case.

        Args:
            channel (str): one or more channels
        """
        self._send_message(messages.join((channel,) + channels))

    def part(self, message, channel, *channels):
        """ Leave the specified channel(s).

        Args:
            message (str): part message
            channel (str): one or more channels
        """
        self._send_message(messages.part((channel,) + channels, message))

    def quit(self, message=None):
        """ Disconnect from the IRC server.

        Also see :py:meth:`handle_disconnect()<.IRCHandler.handle_disconnect`.

        Args:
            message (str): optional message, send to the server
        """
        self._send_message(messages.quit(message))

    def send_message(self, channel, message):
        """ Send a message to a channel.

        Args:
            channel (str): the addressed channel
            message (str): the message to send
        """
        self._send_message(
            messages.privmsg(channel, message, self._state.nick))

    def send_private_message(self, user, message):
        """ Send a private message to a user.

        Args:
            user (str):  the addressed user
            message (str): the message tro send
        """
        if user.startswith('#') or user.startswith('+') or user.startswith('&'):
            self._logger.warn("Detained private message to {} which seems to be"
                              "a channel instead of a user.".format(user))
            return
        self._send_message(
            messages.privmsg(user, message, self._state.nick))

    def pong(self):
        """ Send a pong message to the server. """
        self._send_message(messages.pong(self._state.server))

    def give_op(self, channel, user):
        """ Grant operator rights to a user on a channel.

        If the client is no operator, the server will respond with an
        error message that can be handled via
        :py:meth:`handle_error()<fredirc.IRCHandler.handle_error>`.

        Args:
            channel (str): the channel
            user (str): the affected user
        """
        mode_change = ChannelModeChange(True, ChannelMode.OPERATOR, (user,))
        self._send_message(messages.channel_mode(channel, mode_change))

    def revoke_op(self, channel, user):
        """ Revoke operator rights from user on a channel.

        If the client is no operator, the server will respond with an
        error message that can be handled via
        :py:meth:`handle_error()<fredirc.IRCHandler.handle_error>`.

        Args:
            channel (str): the channel
            user (str): the affected user
        """
        mode_change = ChannelModeChange(False, ChannelMode.OPERATOR, (user,))
        self._send_message(messages.channel_mode(channel, mode_change))

    def give_voice(self, channel, user):
        """ Grant voice rights to a user on a channel.

        If the client is no operator, the server will respond with an
        error message that can be handled via
        :py:meth:`handle_error()<fredirc.IRCHandler.handle_error>`.

        Args:
            channel (str): the channel
            user (str): the affected user
        """
        mode_change = ChannelModeChange(True, ChannelMode.VOICE, (user,))
        self._send_message(messages.channel_mode(channel, mode_change))

    def revoke_voice(self, channel, user):
        """ Revoke voice rights from user on a channel.

        If the client is no operator, the server will respond with an
        error message that can be handled via
        :py:meth:`handle_error()<fredirc.IRCHandler.handle_error>`.

        Args:
            channel (str): the channel
            user (str): the affected user
        """
        mode_change = ChannelModeChange(False, ChannelMode.VOICE, (user,))
        self._send_message(messages.channel_mode(channel, mode_change))

    def is_op_in(self, channel):
        """
        Check if this client has operator rights in the given channel.

        Args:
            channel (str): the channel (case-insensitive)
        """
        return channel.lower() in self._state.operator_in

    def has_voice_in(self, channel):
        """
        Check if this client has voice rights in the given channel.

        Args:
            channel (str): the channel (case-insensitive)
        """
        return channel.lower() in self._state.has_voice_in

    # --- Private methods ---

    def _send_message(self, message):
        """ Send a message to the server.

        Args:
            message (str): A valid IRC message. Only carriage return and line
                           feed are appended automatically.
        """
        self._logger.debug('Sending message: {}'.format(message))
        message += '\r\n'
        self._transport.write(message.encode('utf-8'))

    def _connect(self):
        """ Create a connection to the configured server using asyncio's
        event loop and this IRCClient instance as protocol.
        """
        loop = asyncio.get_event_loop()
        task = asyncio.Task(loop.create_connection(
            self, self._configured_server, self._configured_port))
        try:
            loop.run_until_complete(task)
        except TimeoutError:
            message = ('Cannot connect to server {} on port {}.'
                       'Connection timed out').format(
                self._configured_server,
                self._configured_port)
            self._logger.error(message)
            raise ConnectionTimeoutError(message)

    def _disconnect(self):
        """ Tell the IRCClient that it lost its connection to the server. """
        self._state.connected = False
        self._handler.handle_disconnect()

    def _decoding_error_handler(self, error):
        """ Error handler that is used with the byte.decode() method.

        Does the same as the built-in 'replace' error handler, but logs an
        error message before.

        Args:
            error (UnicodeDecodeError): The error that was raised during decode.
        """
        self._logger.error(
            'Invalid character encoding: {}'.format(error.reason))
        self._logger.error('Replacing the malformed character.')
        return codecs.replace_errors(error)

    # --- Implemented methods from superclasses ---

    def __call__(self):
        """ Returns this IRCClient instance. Used as factory method for 
            BaseEventLoop.create_connection().
        """
        return self

    def connection_made(self, transport):
        """ Implementation of inherited method
            (from :class:`asyncio.Protocol`).
        """
        self._logger.info('Connected to server.')
        self._transport = transport
        self._state.connected = True
        self._handler.handle_connect()

    def connect_lost(self, exc):
        """ Implementation of inherited method
            (from :class:`asyncio.Protocol`).
        """
        self._logger.info('Connection closed.')
        self._disconnect()

    def eof_received(self):
        """ Implementation of inherited method
            (from :class:`asyncio.Protocol`).
        """
        self._logger.debug('Received EOF')
        self._disconnect()

    def data_received(self, data):
        """ Implementation of inherited method
            (from :class:`asyncio.Protocol`).
        """
        try:
            data = data.decode('utf-8', 'log_and_replace')
            data = data.splitlines()
            self._buffer += data
            # ### TODO ###
            # Do we really need to create a copy here?
            # There's probably a better way to allow pop during iteration.
            # Alternatives:
            # 1. Make buffer a byte string (and just append incoming data),
            #    then loop 'while self._buffer', look for terminator and remove
            #    the message.
            # 2. Make buffer a byte string, split lines to list, iterate list,
            #    clear buffer. Con: While handling messageis in loop, buffer
            #    stays the same (empty or with all messages that were received)
            # Con of buffer byte string: more difficult to debug
            #
            tmp_buffer = list(self._buffer)
            for message in tmp_buffer:
                self._logger.debug('Incoming message: {}'.format(message))
                self._processor.process(message)
                self._buffer.pop(0)
        # Shutdown client if unhandled exception occurs, as EventLoop does not
        # provide a handle_error() method so far.
        except Exception as e:
            self._logger.exception(('Unhandled Exception while running an ' +
                                   'IRCClient: {}').format(e))
            self._logger.critical('Shutting down the client, due to an ' +
                                  'unhandled exception!')
            self.terminate()

    def _get_nick(self):
        return self._state.nick

    nick = property(_get_nick)
    """ Current nick name of the client (*read-only*).

    Returns:
        str: nick name or ``None`` if client is not registered
    """
    def _get_server(self):
        return self._state.server

    server = property(_get_server)
    """ Name of the Server this client is currently connected to (*read-only*).

    Returns:
        str: server name or ``None`` if client is not connected to a server.
    """

    def _get_channels(self):
        return tuple(self._state.channels)

    channels = property(_get_channels)
    """ Names of channels this client is currently in (*read-only*).

    Returns:
        tuple: channel names as strings, tuple might be empty
    """


class IRCClientState(object):
    """ Stores the state of an IRCClient.

    This class is **internally** used by IRCClient to keep track of it's
    current state.
    The main purpose is to bundle all the needed information and thus make it
    easier to keep track of them.

    .. note:: The state information in this class should only be set in
              consequence of a message from the server confirming that state.
              For example: The nick should not be set when the client sends a
              nick message, but when it receives a message from the server that
              says the nick has changed.

    To change the state the public properties connected and registered can be
    set directly.
    Note that there are dependencies between the states of the client.
    If a client is registered, it must also be connected and if it is not
    connected it can't be registered. These constraints are preserved
    automatically.

    For example:

    ..code-block:: python

    state = IRCClientState()
    state.connected = True
    state.registered = True
    state.connected = False
    print(state.registered) # False
    state.registered = True
    print(state.connected) # True

    """

    # --- Constants, internally used to set the _state flag ---
    _DISCONNECTED = 0
    _CONNECTED = 1
    _REGISTERED = 2

    def __init__(self):
        self._state = IRCClientState._DISCONNECTED
        self.server = None
        # Note: Nicks in server messages always have the case in which they
        #       were registered.
        self.nick = None
        # Note: Channel names will always be saved lower case
        self.channels = []
        # Channels, where the client is channel operator in:
        self.operator_in = []
        # Channels, where the client has voice rights in:
        self.has_voice_in = []

    # --- Properties that provide an interface to the internal _state flag ---

    @property
    def connected(self):
        return self._state >= IRCClientState._CONNECTED

    @connected.setter
    def connected(self, value):
        if value and self._state < IRCClientState._CONNECTED:
            self._state = IRCClientState._CONNECTED
        elif not value and self._state >= IRCClientState._CONNECTED:
            self._state = IRCClientState._DISCONNECTED
            self._disconnect()

    @property
    def registered(self):
        return self._state == IRCClientState._REGISTERED

    @registered.setter
    def registered(self, value):
        if value:
            self._state = IRCClientState._REGISTERED
        elif not value and self._state == IRCClientState._REGISTERED:
            self._state = IRCClientState._CONNECTED
            self._unregister()

    # --- Private methods ----

    def _unregister(self):
        """ Reset all attributes that require registration to a server. """
        self.nick = None
        self.channels = []
        self.operator_in = []
        self.has_voice_in = []

    def _disconnect(self):
        """ Reset all attributes that require connection to a server. """
        self._unregister()
        self.server = None
