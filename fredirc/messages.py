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


class CmdRepl:
    """ Command Replies """
    RPL_WELCOME = 1


class ErrRepl:
    """ Error Replies """
    ERR_NICKNAMEINUSE = 433


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
