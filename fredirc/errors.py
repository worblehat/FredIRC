# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
Exception classes for FredIRC.
"""

__all__ = ["FredIRCError",
           "MessageHandlingError",
           "ParserError",
           "ConnectionTimeoutError"]

class FredIRCError(Exception):
    """ Base class for FredIrc specific Exceptions. Has a message with further
        description of the error.
    """
    pass


class MessageHandlingError(FredIRCError):
    """ Indicates that the specified message can not be handled by any of the
        normal message handlers.
    """
    pass


class ParserError(FredIRCError):
    """ Indicates that a parser rejects it's input. """
    pass


class ConnectionTimeoutError(FredIRCError):
    """ The connection to a server timed out. """
    pass
