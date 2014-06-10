# Copyright (c) 2013 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD  license.

"""
TODO
"""

import asyncio
import codecs
import logging
import re

from fredirc import messages
from fredirc import parsing
from fredirc.errors import CantHandleMessageError
from fredirc.errors import ConnectionTimeoutError
from fredirc.errors import ParserError
from fredirc.messages import Cmd
from fredirc.messages import CmdRepl
from fredirc.messages import ErrRepl


class IRCClient(asyncio.Protocol):
    """ IRC client class managing the network connection and dispatching
        messages from the server.

    .. warning:: Currently only a single IRCClient instance is allowed! Don't
        run multiple clients. This will result in undefined behaviour. This
        will be fixed in future releases as soon as possible.

    """

    def __init__(self, handler, nick, server, port=6667):
        """ Create an IRCClient instance.

        To connect to the server and start the processing event loop call
        :py:meth:ˋ.IRCClient.runˋ on the instance.
        Args:
            handler (IRCHandler): handler that handles events from this client
            nick (str): nick name for the client
            server (str): server name or ip
            port (int): port number to connect to
        """
        asyncio.Protocol.__init__(self)
        self._handler = handler
        self._state = IRCClientState()
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
        self._connected = False
        self._configured_nick = nick
        self._configured_server = server
        self._configured_port = port
        self._buffer = []
        self._handler.handle_client_init(self)

    def run(self):
        """ Start the IRCClient's event loop.

        An endless event loop which will call the handle_* messages from
        IRCHandler is started. The client connects to the server and
        calls :py:meth:`.IRCHandler.handle_connect` if this is successful.
        To disconnect from the server and terminate the event loop call
        :py:meth:`.IRCClient.quit`.
        """
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            task = asyncio.Task(loop.create_connection(
                self, self._configured_server, self._configured_port))
            try:
                loop.run_until_complete(task)
            except TimeoutError:
                message = "Cannot connect to server " + \
                          self._configured_server + " on port " + \
                          str(self._configured_port) + \
                          ". Connection timed out."
                self._logger.error(message)
                raise ConnectionTimeoutError(message)
            loop.run_forever()

    def enable_logging(self, enable):
        """ Enable or disable logging.

        Args:
            enable (bool)
        """
        if enable:
            self._logger.removeFilter(lambda x: 0)
        else:
            self._logger.addFilter(lambda x: 0)

    def set_log_level(self, level):
        """ Set the log level that is used if logging is enabled.

        Args:
            level (int): the log level as defined by constants in Python's
                         :py:mod:ˋloggingˋ module (DEBUG, INFO, WARNING, ERROR,
                         CRITICAL)
        """
        self._logger.setLevel(level)

    # --- IRC related methods ---

    def register(self):
        """ Register to the IRC server using the nick specified on
            initialization.
        """
        #TODO make username and full name configurable
        #self._send_message(messages.password()) #TODO not needed?
        self._send_message(messages.nick(self._configured_nick))
        self._send_message(messages.user(self._configured_nick, "FredIRC"))

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
            channel (str): one or more channels
        """
        self._send_message(messages.part((channel,) + channels, message))

    def quit(self, message = None):
        """ Disconnect from the IRC server and terminate the IRCClient's event
            loop.

        Args:
            message (str): optional message, send to the server
        """
        self._send_message(messages.quit(message))
        self._shutdown()

    def send_message(self, channel, message):
        """ Send a message to a channel.

        Args:
            channel (str): the channel the message is addressed to
            message (str): the message to send
        """
        self._send_message(
                messages.privmsg(channel, message, self._state.nick))

    def pong(self):
        """ Send a pong message to the server. """
        self._send_message(messages.pong(self._state.server))

    # --- Private methods ---

    def _handle(self, message):
        """ Main message handling method.

        The message is parsed and a command specific handling message is
        called.

        Args:
            message (str): complete, raw message as received from the server.
        """
        assert self._state.connected
        try:
            prefix, command, params = parsing.parse(message)
            three_digits = re.compile('[0-9][0-9][0-9]')
            if three_digits.match(command):
                numeric_reply = int(command)
                if 0 <= numeric_reply <= 399:
                    self._logger.debug('Handling numeric response: ' + command)
                    self._handler.handle_numeric_response(
                            numeric_reply, message)
                    # Call handle_register when we receive welcome message from
                    # server (as response to registration with NICK, USER and
                    # PASS)
                    if numeric_reply == CmdRepl.RPL_WELCOME:
                        self._state.registered = True
                        self._state.server = prefix
                        self._state.nick = params[0]
                        self._handler.handle_register()
                elif 400 <= numeric_reply <= 599:
                    self._logger.debug(
                            'Handling numeric error response: ' + command)
                    self._handler.handle_numeric_error(numeric_reply, message)
                    if numeric_reply == ErrRepl.ERR_NICKNAMEINUSE:
                        self._handler.handle_nick_in_use(params[-2])
                else:
                    self._logger.error('Received numeric response out of ' +
                                       'range: ' + command)
                    raise CantHandleMessageError(message)
            elif command == Cmd.PING:
                if len(params) > 1:
                    self._logger.error('Unexpected count of parameters in '+
                                       command + ' command: ' + message)
                self._logger.debug('Handling ' + command + ' command.')
                self._handler.handle_ping(params[0])
            elif command == Cmd.PRIVMSG:
                self._logger.debug('Handling ' + command + ' command.')
                if not len(params) == 2:
                    raise CantHandleMessageError(message)
                sender = None
                if prefix:
                    sender = parsing.parse_user_prefix(prefix)[0]
                if sender and not sender == self._state.nick:
                    targets = parsing.parse_message_target(params[0])
                    msg = params[1]
                    for target in targets:
                        if target.nick and target.nick == self._state.nick:
                            self._handler.handle_private_message(msg, sender)
                        elif target.channel and \
                             target.channel in self._state.channels:
                            self._handler.handle_channel_message(
                                    target.channel, msg, sender)
            elif command == Cmd.JOIN:
                nick = parsing.parse_user_prefix(prefix)[0]
                channel = params[0]
                if self._state.nick == nick:
                    if not channel in self._state.channels:
                        self._state.channels.append(channel)
                    self._handler.handle_own_join(channel)
                else:
                    self._handler.handle_join(channel, nick)
            elif command == Cmd.PART:
                nick = parsing.parse_user_prefix(prefix)[0]
                channel = params[0]
                if self._state.nick == nick:
                    if channel in self._state.channels:
                        self._state.channels.remove(channel)
                    self._handler.handle_own_part(channel)
                else:
                    self._handler.handle_part(channel, nick)
            else:
                raise CantHandleMessageError(message)
        except CantHandleMessageError as e:
            self._logger.debug('Unhandled message: ' + str(e))
            self._handler.handle_unhandled_message(str(e))
        except ParserError as e:
            self._logger.error('Message Parsing failed. ' + e.message)
            self._logger.error('Message discarded!')

    def _send_message(self, message):
        """ Send a message to the server.

        Args:
            message (str): A valid IRC message. Only carriage return and line
                           feed are appended automatically.
        """
        self._logger.debug('Sending message: ' + message)
        message = message + '\r\n'
        self._transport.write(message.encode('utf-8'))

    def _shutdown(self):
        """ Shutdown the IRCClient by terminating the event loop. """
        self._logger.info('IRCCLient shutting down.')
        self._state.connected = False
        asyncio.get_event_loop().close()
        #TODO More to do? Close Connection gracefully? Beware: shutdown is
        #     called by quit()

    def _decoding_error_handler(self, error):
        """ Error handler that is used with the byte.decode() method.

        Does the same as the built-in 'replace' error handler, but logs an
        error message before.

        Args:
            error (UnicodeDecodeError): The error that was raised during decode.
        """
        self._logger.error('Invalid character encoding: ' + error.reason)
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
        self._shutdown()

    def eof_received(self):
        """ Implementation of inherited method
            (from :class:`asyncio.Protocol`).
        """
        self._logger.debug('Received EOF')
        self._shutdown()

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
                self._logger.debug('Incoming message: ' + message)
                self._handle(message)
                self._buffer.pop(0)
        # Shutdown client if unhandled exception occurs, as EventLoop does not
        # provide a handle_error() method so far.
        except Exception as e:
            self._logger.exception('Unhandled Exception while running an ' +
                                   'IRCClient: ' + str(e))
            self._logger.critical('Shutting down the client, due to an ' +
                                  'unhandled exception!')
            self._shutdown()


class IRCClientState(object):
    """ Stores the state of an IRCClient.

    This class is used by IRCClient to keep track of it's current state. The
    main purpose is to bundle all the needed information and thus make it
    easier to keep track of them.

    .. note:: The state information in this class should only be set in
              consequence of a message from the server confirming that state.
              For example: The nick is not set when the client sends a nick
              message, but when it receives a message from the server that says
              the nick has changed.

    TODO document behaviour of state properties
    TODO document that members are public and the user of this class is
         responsible for ony setting values appropriate to the current state
         (by checking the state before)
    TODO unittests for state properties
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
        # Note: Channel names seem to be always lower case in messages from
        #       the server.
        self.channels = []
        self.mode = None

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
        self.channels = None
        self.mode = None

    def _disconnect(self):
        """ Reset all attributes that require connection to a server. """
        self._unregister()
        self.server = None
