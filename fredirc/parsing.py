# Copyright (c) 2013 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD  license.

"""
This module provides functions for parsing of irc messages.
This is not an implementation of a complete parser but just 
functions that parse specific (parts of) irc messages and extract some
information for further processing. Parsing errors might be raised on invalid
input, but an accepted input does not automatically mean that it conforms to
the irc message grammar (as described in RFC 2812).
"""

from fredirc.errors import ParserError


def parse(message):
    """
    Parse a message and return a triple containing prefix, command and
    paramaters.
    Relevant part of the protocol's grammar:
       message    =  [ ":" prefix SPACE ] command [ params ] crlf
       command    =  1*letter / 3digit
       params     =  *14( SPACE middle ) [ SPACE ":" trailing ]
                  =/ 14( SPACE middle ) [ SPACE [ ":" ] trailing ]
    Prefix and parameters may be None. On the prefix and so called 'trailing'
    parameters (i.e. parameters with whitespaces) the leading colon as well as
    leading and trailing whitespaces are removed.
    :param message: Raw irc message (without the CRLF)
    :type message: str
    :return: 3-element tuple
    :rtype: two strings (prefix and command) and a tuple of strings (params)
    """
    prefix = None
    params = None
    # Prefix
    if message.startswith(':'):
        try:
            prefix, message = message.split(None, 1)
        except ValueError:
            raise ParserError('Malformed message: ' + message)
        prefix = prefix[1:]
    # Command
    try:
        tmp_split = message.split(None, 1)
    except ValueError:
        raise ParserError('Malformed message: ' + message)
    command = tmp_split[0]
    # Parameters
    if len(tmp_split) == 2:
        param_split = tmp_split[1].split(':')
        params_trailing = param_split[1:]
        params_middle = param_split[0].split()
        params_trailing = [param.strip() for param in params_trailing
                           if len(param) > 0]
        params = params_middle + params_trailing
    return (prefix, command, params)


def parse_user_prefix(prefix):
    """
    Parses:
        prefix = nickname [ [ "!" user ] "@" host ]
    :return: triple (nick, user, host), user and host might be None
    :rtype: triple of str
        """
    user = None
    host = None
    nick = prefix
    host_split = prefix.split('@', 1)
    if len(host_split) == 2:
        nick = host_split[0]
        host = host_split[1]
        user_split = nick.split('!', 1)
        if len(user_split) == 2:
            nick = user_split[0]
            user = user_split[1]
    return nick, user, host

def parse_message_target(msg_target):
    """
    Parses:
      msgtarget  =  msgto *( "," msgto )
      msgto      =  channel / ( user [ "%" host ] "@" servername )
      msgto      =/ ( user "%" host ) / targetmask
      msgto      =/ nickname / ( nickname "!" user "@" host )
      channel    =  ( "#" / "+" / ( "!" channelid ) / "&" ) chanstring
                    [ ":" chanstring ]
    :return: MessageTargets, where each MessageTarget represents one 'msgto'
             from the grammar rule
    :rtype: tuple of MessageTarget
    """
    targets = list()
    targets_split = msg_target.split(',')
    for msgto in targets_split:
        # TODO does not completely implement the specs
        #      (no channel ids and collon delimiters)
        if msgto.startswith('#') or \
           msgto.startswith('+') or \
           msgto.startswith('&'):
            mt = MessageTarget(channel=msgto)
        elif '@' in msgto:
            user_split = msgto.split('@', 1)
            if '!' in user_split[0]:
                nick_split = user_split[0].split('!', 1)
                mt = MessageTarget(nick=nick_split[0], user=nick_split[1],
                                   host=user_split[1])
            else:
                if '%' in user_split[0]:
                    host_split = user_split[0].split('%', 1)
                    mt = MessageTarget(user=host_split[0], host=host_split[1],
                                       server=user_split[1])
                else:
                    mt = MessageTarget(user=user_split[0],
                                       server=user_split[1])
        elif '%' in msgto:
            user_split = msgto.split('%', 1)
            mt = MessageTarget(user=user_split[0], host=user_split[1])
        elif (msgto.startswith('$') or msgto.startswith('#')) and '.' in msgto:
            mt = MessageTarget(target_mask=msgto)
        else:
            mt = MessageTarget(nick=msgto)
        targets.append(mt)
    return tuple(targets)


class MessageTarget(object):
    """
    Represents a target of an IRC message. Corresponds to the non-terminal
    'msgto' in IRC's grammer.
    """

    def __init__(self, channel=None, nick=None, user=None, host=None,
                 server=None, target_mask=None):
        self.channel = channel
        self.nick = nick
        self.user = user
        self.host = host
        self.server = server
        self.target_mask = target_mask
