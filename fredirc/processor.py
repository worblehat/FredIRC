# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
This module contains the MessageProcessor.
"""

__all__ = []

import re

from fredirc import parsing
from fredirc.errors import MessageHandlingError
from fredirc.errors import ParserError
from fredirc.messages import ChannelMode
from fredirc.messages import Cmd
from fredirc.messages import Rpl
from fredirc.messages import Err


class MessageProcessor(object):
    """ Processes raw messages from the server and takes appropriate action.

    Messages are parsed, the client's state is modified if needed and the
    registered :py:class:`IRCHandler` is notified.
    """

    def __init__(self, handler, state, logger):
        self._handler = handler
        self._state = state
        self._logger = logger

    def process(self, message):
        """ Main message processing method.

        The message is parsed and a command specific handling method is
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
                    self._process_numeric_reply(
                        numeric_reply, prefix, params, message)
                elif 400 <= numeric_reply <= 599:
                    self._process_numeric_error(numeric_reply, params, message)
                else:
                    self._logger.error(('Received numeric response out of ' +
                                       'range: {}').format(command))
                    raise MessageHandlingError(message)
            elif command == Cmd.PING:
                self._process_ping(params, message)
            elif command == Cmd.PRIVMSG:
                self._process_privmsg(prefix, params, message)
            elif command == Cmd.JOIN:
                self._process_join(prefix, params)
            elif command == Cmd.PART:
                self._process_part(prefix, params)
            elif command == Cmd.MODE:
                self._process_mode(prefix, params, message)
            elif command == Cmd.KICK:
                self._process_kick(prefix, params)
            else:
                raise MessageHandlingError(message)
        except MessageHandlingError as e:
            self._logger.debug('Unhandled message: {}'.format(e))
            self._handler.handle_unhandled_message(str(e))
        except ParserError as e:
            self._logger.error('Message Parsing failed. {}'.format(e.message))
            self._logger.error('Message discarded!')

    def _process_ping(self, params, raw_msg):
        if len(params) > 1:
            self._logger.error(('Unexpected count of parameters in PING ' +
                               'command: {}').format(raw_msg))
        self._handler.handle_ping(params[0])

    def _process_privmsg(self, prefix, params, raw_msg):
        if not len(params) == 2:
            raise MessageHandlingError(raw_msg)
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

    def _process_numeric_reply(self, num, prefix, params, raw_msg):
        self._handler.handle_response(num, raw_msg)
        # Call handle_register when we receive welcome message from
        # server (as response to registration with NICK, USER and
        # PASS)
        if num == Rpl.WELCOME:
            self._state.registered = True
            self._state.server = prefix
            self._state.nick = params[0]
            self._handler.handle_register()

    def _process_numeric_error(self, num, params, raw_msg):
        # Remove the first parameter which is always the message target
        params = params[1:]
        param_names = Err.ERROR_PARAMETERS[num]
        kwargs = {}
        if len(params) != len(param_names):
            self._logger.error(('Unexpected number of parameters in error ' +
                               'code message ({})').format(num))
            # Make sure all parameter keys are present in kwargs anyway and
            # put all received params in the "message" value if there is one.
            for name in param_names:
                kwargs[name] = ' '.join(params) if name == 'message' else ''
        else:
            for name, value in zip(param_names, params):
                kwargs[name] = value
        self._handler.handle_error(num, **kwargs)

    def _process_join(self, prefix, params):
        nick = parsing.parse_user_prefix(prefix)[0]
        channel = params[0]
        if self._state.nick == nick:
            if channel not in self._state.channels:
                self._state.channels.append(channel)
            self._handler.handle_own_join(channel)
        else:
            self._handler.handle_join(channel, nick)

    def _process_part(self, prefix, params):
        nick = parsing.parse_user_prefix(prefix)[0]
        channel = params[0]
        if self._state.nick == nick:
            if channel in self._state.channels:
                self._state.channels.remove(channel)
            self._handler.handle_own_part(channel)
        else:
            part_message = None
            if len(params) > 1:
                part_message = params[1]
            self._handler.handle_part(channel, nick, part_message)

    def _process_mode(self, prefix, params, raw_msg):
        target = parsing.parse_message_target(params[0])[0]
        initiator = parsing.parse_user_prefix(prefix)[0]
        if target.channel:  # Channel Mode
            self._process_channel_mode(target.channel, params[1:], initiator)
        elif target.nick:  # User Mode
            # User modes not yet implemented
            # self._process_user_mode(target.nick, params[1:])
            raise MessageHandlingError(raw_msg)
        else:
            raise MessageHandlingError(raw_msg)

    def _process_channel_mode(self, channel, params, initiator):
        mode_changes = parsing.parse_channel_mode_params(params)
        for mode_change in mode_changes:
            # Look for channel modes that affect users
            if mode_change.mode == ChannelMode.OPERATOR:
                user = mode_change.params[0]
                if mode_change.added:
                    self._state.operator_in.append(channel)
                    self._handler.handle_got_op(channel, user, initiator)
                else:
                    self._state.operator_in.remove(channel)
                    self._handler.handle_lost_op(channel, user, initiator)
            elif mode_change.mode == ChannelMode.VOICE:
                user = mode_change.params[0]
                if mode_change.added:
                    self._state.has_voice_in.append(channel)
                    self._handler.handle_got_voice(channel, user, initiator)
                else:
                    self._state.has_voice_in.remove(channel)
                    self._handler.handle_lost_voice(channel, user, initiator)

    def _process_kick(self, prefix, params):
        if len(params) < 2:
            return  # TODO how to handle malformed messages in processor?
        channel = params[0]
        initiator = parsing.parse_user_prefix(prefix)[0]
        reason = params[2] if len(params) > 2 else None
        if channel in self._state.channels:
            self._state.channels.remove(channel)
        self._handler.handle_kick(channel, params[1], initiator, reason)
