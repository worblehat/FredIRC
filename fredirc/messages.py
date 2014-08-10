# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
Low level functions for creation of irc client messages, as well as classes
with constants for string commands, numeric commands and error responses.
Specification: RFC 2812 'IRC: Client Protocol'.
"""


class Cmd:
    """ Commands """

    # Message Registration
    PASS = 'PASS'
    NICK = 'NICK'
    USER = 'USER'
    QUIT = 'QUIT'
    # Channel Operations
    JOIN = 'JOIN'
    PART = 'PART'
    # Sending Messages
    PRIVMSG = 'PRIVMSG'
    # Miscellaneous
    PING = 'PING'
    PONG = 'PONG'


class Rpl:
    """ Command Replies """
    WELCOME = 1


class Err:
    """ Error Replies """

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
        NOSUCHNICK : ['nick', 'message'],
        NOSUCHSERVER : ['server_name', 'message'],
        NOSUCHCHANNEL : ['channel_name', 'message'],
        CANNOTSENDTOCHAN : ['channel_name', 'message'],
        TOOMANYCHANNELS : ['channel_name', 'message'],
        WASNOSUCHNICK : ['nick', 'message'],
        TOOMANYTARGETS : ['target', 'message'],
        NOSUCHSERVICE : ['service_name', 'message'],
        NOORIGIN : ['message'],
        NORECIPIENT : ['message'],
        NOTEXTTOSEND : ['message'],
        NOTOPLEVEL : ['mask', 'message'],
        WILDTOPLEVEL : ['mask', 'message'],
        BADMASK : ['mask', 'message'],
        UNKNOWNCOMMAND : ['command', 'message'],
        NOMOTD : ['message'],
        NOADMININFO : ['server', 'message'],
        FILEERROR : ['message'],
        NONICKNAMEGIVEN : ['message'],
        ERRONEUSNICKNAME : ['nick', 'message'],
        NICKNAMEINUSE : ['nick', 'message'],
        NICKCOLLISION : ['nick', 'message'],
        UNAVAILRESOURCE : ['nick', 'message'],
        USERNOTINCHANNEL : ['nick', 'channel', 'message'],
        NOTONCHANNEL : ['channel', 'message'],
        USERONCHANNEL : ['user', 'channel', 'message'],
        NOLOGIN : ['user', 'channel', 'message'],
        SUMMONDISABLED : ['message'],
        USERSDISABLED : ['message'],
        NOTREGISTERED : ['message'],
        NEEDMOREPARAMS : ['command', 'message'],
        ALREADYREGISTRED : ['message'],
        NOPERMFORHOST : ['message'],
        PASSWDMISMATCH : ['message'],
        YOUREBANNEDCREEP : ['message'],
        YOUWILLBEBANNED : [],
        KEYSET : ['channel', 'message'],
        CHANNELISFULL : ['channel', 'message'],
        UNKNOWNMODE : ['mode', 'message'],
        INVITEONLYCHAN : ['channel', 'message'],
        BANNEDFROMCHAN : ['channel', 'message'],
        BADCHANNELKEY : ['channel', 'message'],
        BADCHANMASK : ['channel', 'message'],
        NOCHANMODES : ['channel', 'message'],
        BANLISTFULL : ['channel', 'message'],
        NOPRIVILEGES : ['message'],
        CHANOPRIVSNEEDED : ['channel', 'message'],
        CANTKILLSERVER : ['message'],
        RESTRICTED : ['message'],
        UNIQOPPRIVSNEEDED : ['message'],
        NOOPERHOST : ['message'],
        UMODEUNKNOWNFLAG : ['message'],
        USERSDONTMATCH : ['message'],
    }

def nick(name):
    return Cmd.NICK + ' ' + name


def password(password=None):
    if password:
        return Cmd.PASS + ' :' + password
    else:
        return Cmd.PASS


def user(user, real_name, invisible=False, receive_wallops=False):
    # TODO set mode correctly
    mode = 0
    return Cmd.USER + ' ' + user + ' ' + str(mode) + ' * :' + real_name


def quit(message=None):
    if message:
        return Cmd.QUIT + ' :' + message
    else:
        return Cmd.QUIT


def join(channels):
    return Cmd.JOIN + ' ' + ','.join(channels)


def pong(server):
    return Cmd.PONG + ' :' + server


def privmsg(target, message, sender=None):
    if not sender:
        sender = ''
    return ':' + sender + ' ' + Cmd.PRIVMSG + ' ' + target + ' :' + message

def part(channels, message):
    return Cmd.PART + ' ' + ','.join(channels) + ' :' + message
