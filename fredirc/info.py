# Copyright (c) 2015 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
Classes that provide some irc-related (read-only) information.
"""

__all__ = ['ChannelInfo']

import collections


class ChannelInfo(object):
    """ Provides information about a channel.

    A ChannelInfo object is a view on a channel and is automatically updated
    as long as the client is in the channel. Afterwards the ChannelInfo becomes
    invalid and should not be used any longer.
    """

    def __init__(self, name):
        self._name = name
        self._topic = ""
        self._nicks = set()

    def _add_nicks(self, *nicks):
        self._nicks.update(nicks)

    def _remove_nick(self, nick):
        try:
            self._nicks.remove(nick)
        except KeyError:
            pass

    def _set_topic(self, topic):
        self._topic = topic

    def _get_topic(self):
        return self._topic

    def _get_name(self):
        return self._name

    def _get_nicks(self):
        return iter(self._nicks)

    name = property(_get_name)
    """ Name of the channel (*read-only*).

    Returns:
        str: name
    """

    topic = property(_get_topic)
    """ Topic of the channel (*read-only*).

    Returns:
        str: topic, might be empty
    """

    nicks = property(_get_nicks)
    """ Nicks of all visible users in this channel. (*read-only*).

    Returns:
        iterator: over nick names
    """


class _ReadOnlyDict(collections.Mapping):
    """ A mapping that serves as a read-only view on a dict.
    """

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()


