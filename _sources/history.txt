Changelog
=========

v0.3.0 (2015-12-09)
-------------------

**Attention**: This release contains some backward-incompatible changes (marked with **(!)** below).

* ChannelInfo-class with information about a channel like current topic and members

  * access via IRCClient.channel_info

* changing the nick name of the client
* handle nick changes
* handle quits
* handle changes to operator- and voice-status
* introduced handle_own_kick()-method

  * **(!)** when the bot gets kicked, this can only be handled in
    handle_own_kick() instead of handle_kick() now

* optional delay for channel messages
* the delay of a Task can be changed now
* **(!)** IRCClient.channels now returns an iterator instead of a tuple

v0.2.2 (2015-04-11)
-------------------

* bug fix: client tried to process partially received messages
* bug fix: processing of operator- and voice-mode changes resulted in inconsistent data structures

v0.2.1 (2015-04-10)
-------------------

* bug fix: the bot no longer received messages from a channel after another user got kicked from it

v0.2.0 (2015-03-05)
-------------------

* handling disconnects
* ability to reconnect to the server
* IRCClient can be terminated manually
* handling changes to channel modes operator and voice
* changing channel modes operator and voice
* sending private messages
* handling kicks and kick other users from channels

v0.1.0 (2014-12-30)
-------------------

* basic handling methods (messages, joins, parts, numeric responses and errors)
* connecting to a single server
* joining multiple channels
* sending channel messages
* scheduling delayed and periodic tasks
