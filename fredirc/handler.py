# Copyright (c) 2013 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD  license.

"""
TODO
"""


class IRCHandler(object):
    """ Abstract base class for IRC handler classes.

    This abstract base class contains handler functions for IRC related events
    (mostly messages from a server) a client might be interested in. It just
    defines an interface and all method bodies are empty.
    You probably want to subclass :py:class:`.BaseIRCHandler` instead of
    inheriting directly from this class.
    TODO write class BaseIRCHandler (if not document auto-response to ping and
         client member)
    """

    def handle_connect(self):
        """ The client established a connection to the server and registration
            succeeded.
        """
        pass

    def handle_ping(self, server):
        """ Received a ping message from the server.

        Args:
            server (str): name or ip of the server.
        """
        self.client.pong()

    def handle_numeric_response(self, response, message):
        """ A numeric response was received from the server.

        See the IRC client protocol specification for valid numeric response
        codes and their meaning. There are extra handler methods for many
        common responses, but this general handler is always called first.

        Args:
            response (int): 3-digit response code (between 0 and 399)
            message (str): the whole, raw message
        """
        pass

    def handle_numeric_error(self, error, message):
        """ A numeric error was received from the server.

        See the IRC client protocol specification for valid numeric error codes
        and their meaning. There are extra handler methods for many common
        errors, but this general handler is always called first.

        Args:
            error (int): 3-digit error code (between 400 and 599)
            message (str): the whole received message
        """
        pass

    def handle_channel_message(self, channel, message, sender=None):
        """ Received a message to a channel.

        A message was sent to a channel the client currently belongs to.
        Does not include messages from the client itself!

        Args:
            channel (str): the channel name
            message (str): the received message
            sender (str): Sender of the message, usually a nickname.
                          Might be None.
        """
        pass

    def handle_private_message(self, message, sender=None):
        """ Received private message (query).

        Args:
            message (str): the received message
            sender (str): Sender of the message, usually a nickname.
                          Might be None.
        """
        pass

    def handle_nick_in_use(self, nick):
        """ The chosen nick is already in use on this server.

        If this event is received while connecting to a server (i.e. before
        :py:meth:`.handle_connect` is called) another nick should be chosen
        before the connection times out. (See :py:meth:`.IRCClient.nick`.)

        Args:
            nick (str): the nick name that is already in use
        """
        pass

    def handle_join(self, channel, nick):
        """ Called when 'nick' joined the 'channel'.

        To handle joins of the IRCClient itself, use
        :py:meth:`.handle_own_join`.

        Args:
            channel (str): a name of a channel, the client is currently in
            nick (str): nick of the member that joined the channel
        """
        pass

    def handle_own_join(self, channel):
        """ Called when the IRCClient joined a channel.

        To handle joins of other members, use :py:meth:`.handle_join`.

        Args:
            channel (str): name of the channel
        """
        pass

    def handle_part(self, channel, nick):
        """ Called when 'nick' left the 'channel'.

        To handle partings of the IRCClient itself, use
        :py:meth:`.handle_own_part`.

        Args:
            channel (str): a name of a channel, the client is currently in
            nick (str): nick of the member that left the channel
        """
        pass

    def handle_own_part(self, channel):
        """ Called when the IRCClient left a channel.

        To handle parting of other members, use :py:meth:`.handle_part`.

        Args:
            channel (str): name of the channel
        """
        pass

    def handle_unhandled_message(self, message):
        """ This handler is called whenever a message is not handled by any
            other handler.

        A message is not handled if either the message is not yet supported by
        FredIRC or it is invalid/malformed.

        Args:
            message (str): The raw message as received by the client.
        """
        pass


