# Copyright (c) 2013 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD  license.

"""
Exception classes for FredIrc.

TODO Move these classes to the modules they belong to?
TODO Consistent naming scheme for errors.
"""


class FredIRCError(Exception):
    """ Base class for FredIrc specific Exceptions. Has a message with further
        description of the error.
    """
    pass

class CantHandleMessageError(FredIRCError):
    """ Indicates that the specified message can not be handled by any of the
        normal message handlers.
    """
    pass


class ParserError(FredIRCError):
    """ Indicates that a parser rejects it's input. """
    pass

class ConnectionTimeoutError(FredIRCError):
    """ The connection to a server timed out. """
