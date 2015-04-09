# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
Abstract IRC-Handler classes that handle IRC related events from a client.
You probably want to subclass :py:class:`.BaseIRCHandler` to implement a bot.
"""

__all__ = ['BaseIRCHandler',
           'IRCHandler']


class IRCHandler(object):
    """ Abstract base class for IRC handler classes.

    This abstract base class contains handler functions for IRC related events
    (mostly messages from a server) a client might be interested in. It just
    defines an interface and all method bodies are empty.
    You probably want to subclass :py:class:`.BaseIRCHandler` instead of
    inheriting directly from this class.
    """

    def handle_client_init(self, client):
        """ This handler was attached to a client.

        Args:
            client (:py:class:`.IRCClient`): The client.
        """
        pass

    def handle_connect(self):
        """ The client established a connection to the server. """
        pass

    def handle_disconnect(self):
        """ The client lost connection to the server.

        This might be the result of a network error but also occurs after
        a quit by the client or a forced disconnect by the server.
        """
        pass

    def handle_register(self):
        """ The client successfully registered to the server. """
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

    def handle_join(self, channel, nick):
        """ Called when a user joined the channel.

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

    def handle_part(self, channel, nick, message=None):
        """ Called when a user left the channel.

        To handle partings of the IRCClient itself, use
        :py:meth:`.handle_own_part`.

        Args:
            channel (str): a name of a channel, the client is currently in
            nick (str): nick of the member that left the channel
            message (str): part message of the parting member (might be None)
        """
        pass

    def handle_own_part(self, channel):
        """ Called when the IRCClient left a channel.

        To handle parting of other members, use :py:meth:`.handle_part`.

        Args:
            channel (str): name of the channel
        """
        pass

    def handle_kick(self, channel, nick, initiator, reason):
        """ A user got kicked from a channel.

        Might be the IRCClient itself.

        Args:
            channel (str): the channel
            nick (str): the user who got kicked
            reason (str): reason for the kick (might be None)
        """
        pass

    def handle_got_op(self, channel, nick, initiator):
        """ A user received operator status.

        Args:
            channel (str): name of the channel
            nick (str): the user who became operator
            initiator (str): the user who granted the operator rights
        """
        pass

    def handle_lost_op(self, channel, nick, initiator):
        """ A user lost operator status.

        Args:
            channel (str): name of the channel
            nick (str): the user who is no longer operator
            initiator (str): the user who initiated the mode change
        """
        pass

    def handle_got_voice(self, channel, nick, initiator):
        """ A user received voice rights.

        Args:
            channel (str): name of the channel
            nick (str): the user who received voice
            initiator (str): the user who granted the voice rights
        """
        pass

    def handle_lost_voice(self, channel, nick, initiator):
        """ A user lost voide rights.

        Args:
            channel (str): name of the channel
            nick (str): the user who no longer has voice
            initiator (str): the user who initiated the mode change
        """
        pass

    def handle_response(self, response, message):
        """ A numeric response was received from the server.

        See the IRC client protocol specification for valid numeric response
        codes and their meaning. There are extra handler methods for many
        common responses, but this general handler is always called first.

        Args:
            response (int): 3-digit response code (between 0 and 399)
            message (str): the whole, raw message
        """
        pass

    def handle_error(self, error, **params):
        """ An irc error message was received from the server.

        The error codes are defined in :py:class:`Err<fredirc.Err>`.
        The contents of the params dictionary depend on the specific error.
        See the documentation of :py:class:`Err<fredirc.Err>` for details.

        Args:
            error (int): 3-digit error code (between 400 and 599)
            params (dict): Parameters of the error message, each consisting of \
                a parameter name and a value.
        """
        pass

    def handle_ping(self, server):
        """ Received a ping message from the server.

        Args:
            server (str): name or ip of the server.
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


class BaseIRCHandler(IRCHandler):
    """ Minimal :py:class:`.IRCHandler` implementation.

    Implements the most basic handler functionality that probably every bot will
    need. It is recommended to subclass :py:class:`.BaseIRCHandler` instead
    of :py:class:`.IRCHandler`.

    What it does for you:

    * Store the :py:class:`.IRCClient` instance as attribute ``self.client`` \
        on :py:meth:`.handle_client_init`.
    * Register to the server on :py:meth:`.handle_connect`.
    * Respond with pong on :py:meth:`.handle_ping`.
    """

    def handle_client_init(self, client):
        self.client = client

    def handle_connect(self):
        self.client.register()

    def handle_ping(self, server):
        self.client.pong()
