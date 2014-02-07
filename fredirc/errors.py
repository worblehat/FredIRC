# Copyright (c) 2013 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD  license.

"""
Exception classes for FredIrc.

TODO Move these classes to the modules they belong to?
"""


class FredIRCError(Exception):
    """ Base class for FredIrc specific Exceptions. Has a message with further description of the error. """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class CantHandleMessageError(FredIRCError):
    """ Indicates that the specified message can not be handled by any of the normal message handlers. """

    def __init__(self, message):
        super().__init__(message)


class ParserError(FredIRCError):
    """ Indicates that a parser rejects it's input. """

    def __init__(self, message):
        super().__init__(message)


class NotConnectedError(FredIRCError):
    """ TODO """ 

    def __init__(self, message):
        super().__init__(message)

