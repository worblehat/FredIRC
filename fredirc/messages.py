# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
Low level functions for creation of irc client messages, as well as classes
with constants for string commands, numeric commands and error responses.
Specification: RFC 2812 'IRC: Client Protocol'.
"""

__all__ = ['Err']


class Cmd:
    """ Commands """

    # Message Registration
    PASS = 'PASS'
    NICK = 'NICK'
    USER = 'USER'
    QUIT = 'QUIT'
    MODE = 'MODE'
    # Channel Operations
    JOIN = 'JOIN'
    PART = 'PART'
    KICK = 'KICK'
    # Sending Messages
    PRIVMSG = 'PRIVMSG'
    # Miscellaneous
    PING = 'PING'
    PONG = 'PONG'


class UserMode:
    """ User Modes

    User modes apply server-wide. So user mode 'o' should not be confused
    with channel mode 'o'.
    """
    AWAY = 'a'
    INVISIBLE = 'i'
    WALLOPS_RECEIVER = 'w'
    RESTRICTED = 'r'
    OPERATOR = 'o'
    LOCAL_OPERATOR = 'O'
    NOTICES_RECEIVER = 's'


class ChannelMode:
    """ Channel Modes """
    # Channel modes affecting a single user
    OPERATOR = 'o'
    VOICE = 'v'
    # Channel modes affecting the channel itself
    # Not yet implemented...


class Rpl:
    """ Command Replies """
    WELCOME = 1
    NAMREPLY = 353
    ENDOFNAMES = 366
    TOPIC = 332


class Err:
    """ Error Replies

    Contains numerical constants for errors as defined by the irc client
    protocol as well as the keywords of error specific parameters.
    Error numbers and parameters are passed to
    :py:meth:`handle_error(self, error, **params)<fredirc.IRCHandler.handle_error()>`.
    You can take a look at :py:attr:`.ERROR_PARAMETERS` to find out the
    parameter keywords for a particular error.

    See the :ref:`beginner's guide<guide_handle-errors>` for an example on how
    to use this class to handle errors.
    """

    NOSUCHNICK = 401
    NOSUCHSERVER = 402
    NOSUCHCHANNEL = 403
    CANNOTSENDTOCHAN = 404
    TOOMANYCHANNELS = 405
    WASNOSUCHNICK = 406
    TOOMANYTARGETS = 407
    NOSUCHSERVICE = 408
    NOORIGIN = 409
    NORECIPIENT = 411
    NOTEXTTOSEND = 412
    NOTOPLEVEL = 413
    WILDTOPLEVEL = 414
    BADMASK = 415
    UNKNOWNCOMMAND = 421
    NOMOTD = 422
    NOADMININFO = 423
    FILEERROR = 424
    NONICKNAMEGIVEN = 431
    ERRONEUSNICKNAME = 432
    NICKNAMEINUSE = 433
    NICKCOLLISION = 436
    UNAVAILRESOURCE = 437
    USERNOTINCHANNEL = 441
    NOTONCHANNEL = 442
    USERONCHANNEL = 443
    NOLOGIN = 444
    SUMMONDISABLED = 445
    USERSDISABLED = 446
    NOTREGISTERED = 451
    NEEDMOREPARAMS = 461
    ALREADYREGISTRED = 462
    NOPERMFORHOST = 463
    PASSWDMISMATCH = 464
    YOUREBANNEDCREEP = 465
    KEYSET = 467
    YOUWILLBEBANNED = 466
    CHANNELISFULL = 471
    UNKNOWNMODE = 472
    INVITEONLYCHAN = 473
    BANNEDFROMCHAN = 474
    BADCHANNELKEY = 475
    BADCHANMASK = 476
    NOCHANMODES = 477
    BANLISTFULL = 478
    NOPRIVILEGES = 481
    CHANOPRIVSNEEDED = 482
    CANTKILLSERVER = 483
    RESTRICTED = 484
    UNIQOPPRIVSNEEDED = 485
    NOOPERHOST = 491
    UMODEUNKNOWNFLAG = 501
    USERSDONTMATCH = 502

    ERROR_PARAMETERS = {
        NOSUCHNICK: ['nick', 'message'],
        NOSUCHSERVER: ['server_name', 'message'],
        NOSUCHCHANNEL: ['channel_name', 'message'],
        CANNOTSENDTOCHAN: ['channel_name', 'message'],
        TOOMANYCHANNELS: ['channel_name', 'message'],
        WASNOSUCHNICK: ['nick', 'message'],
        TOOMANYTARGETS: ['target', 'message'],
        NOSUCHSERVICE: ['service_name', 'message'],
        NOORIGIN: ['message'],
        NORECIPIENT: ['message'],
        NOTEXTTOSEND: ['message'],
        NOTOPLEVEL: ['mask', 'message'],
        WILDTOPLEVEL: ['mask', 'message'],
        BADMASK: ['mask', 'message'],
        UNKNOWNCOMMAND: ['command', 'message'],
        NOMOTD: ['message'],
        NOADMININFO: ['server', 'message'],
        FILEERROR: ['message'],
        NONICKNAMEGIVEN: ['message'],
        ERRONEUSNICKNAME: ['nick', 'message'],
        NICKNAMEINUSE: ['nick', 'message'],
        NICKCOLLISION: ['nick', 'message'],
        UNAVAILRESOURCE: ['nick', 'message'],
        USERNOTINCHANNEL: ['nick', 'channel', 'message'],
        NOTONCHANNEL: ['channel', 'message'],
        USERONCHANNEL: ['user', 'channel', 'message'],
        NOLOGIN: ['user', 'channel', 'message'],
        SUMMONDISABLED: ['message'],
        USERSDISABLED: ['message'],
        NOTREGISTERED: ['message'],
        NEEDMOREPARAMS: ['command', 'message'],
        ALREADYREGISTRED: ['message'],
        NOPERMFORHOST: ['message'],
        PASSWDMISMATCH: ['message'],
        YOUREBANNEDCREEP: ['message'],
        YOUWILLBEBANNED: [],
        KEYSET: ['channel', 'message'],
        CHANNELISFULL: ['channel', 'message'],
        UNKNOWNMODE: ['mode', 'message'],
        INVITEONLYCHAN: ['channel', 'message'],
        BANNEDFROMCHAN: ['channel', 'message'],
        BADCHANNELKEY: ['channel', 'message'],
        BADCHANMASK: ['channel', 'message'],
        NOCHANMODES: ['channel', 'message'],
        BANLISTFULL: ['channel', 'message'],
        NOPRIVILEGES: ['message'],
        CHANOPRIVSNEEDED: ['channel', 'message'],
        CANTKILLSERVER: ['message'],
        RESTRICTED: ['message'],
        UNIQOPPRIVSNEEDED: ['message'],
        NOOPERHOST: ['message'],
        UMODEUNKNOWNFLAG: ['message'],
        USERSDONTMATCH: ['message'],
    }


def nick(name):
    return '{nick_cmd} {name}'.format(
            nick_cmd=Cmd.NICK, name=name)


def password(pwd=None):
    if pwd:
        return '{pass_cmd} :{password}'.format(
                pass_cmd=Cmd.PASS, password=pwd)
    else:
        return Cmd.PASS


def user(user_name, real_name, invisible=False, receive_wallops=False):
    # TODO set mode correctly
    mode = 0
    return '{user_cmd} {user} {mode} * :{real_name}'.format(
            user_cmd=Cmd.USER, user=user_name, mode=mode, real_name=real_name)


def quit(message=None):
    if message:
        return '{quit_cmd} :{message}'.format(
                quit_cmd=Cmd.QUIT, message=message)
    else:
        return Cmd.QUIT


def join(channels):
    return '{join_cmd} {channels}'.format(
            join_cmd=Cmd.JOIN, channels=','.join(channels))


def pong(server):
    return '{pong_cmd} :{server}'.format(
            pong_cmd=Cmd.PONG, server=server)


def privmsg(target, message, sender=None):
    if not sender:
        sender = ''
    return ':{sender} {msg_cmd} {target} :{message}'.format(
            sender=sender, msg_cmd=Cmd.PRIVMSG, target=target, message=message)


def part(channels, message):
    return '{part_cmd} {channels} :{message}'.format(
            part_cmd=Cmd.PART, channels=','.join(channels), message=message)


def kick(channels, users, message=None):
    if not message:
        message = ''
    return '{kick_cmd} {channels} {users} :{message}'.format(
        kick_cmd=Cmd.KICK, channels=','.join(channels), users=','.join(users),
        message=message)


def channel_mode(channel, mode_change):
    """
    Args:
        mode_change (ChannelModelChange)
    """
    change = '+' if mode_change.added else '-'
    return '{mode_cmd} {channel} {change}{mode} {params}'.format(
            mode_cmd=Cmd.MODE, channel=channel, change=change,
            mode=mode_change.mode, params=' '.join(mode_change.params))