# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
Exception classes for FredIRC.
"""

__all__ = ['FredIRCError',
           'MessageHandlingError',
           'ParserError',
           'ConnectionTimeoutError']


class FredIRCError(Exception):
    """ Base class for FredIRC specific Exceptions. Contains a message with further
        description of the error.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class MessageHandlingError(FredIRCError):
    """ Indicates that the specified message can not be handled by any of the
        normal message handlers.
    """
    pass


class ParserError(FredIRCError):
    """ Indicates that a parser rejects its input. """
    pass


class ConnectionTimeoutError(FredIRCError):
    """ The connection to a server timed out. """
    pass
