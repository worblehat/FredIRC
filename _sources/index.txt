Welcome to FredIRC's Homepage!
==============================

FredIRC is an event-driven Python framework for
`IRC (Internet Relay Chat) <http://en.wikipedia.org/wiki/Internet_Relay_Chat>`_
bots. It aims to provide a high-level abstraction of
`IRC's internals <http://tools.ietf.org/search/rfc2812>`_, an easy-to-use API
and convinient utilities related to bot development.

FredIRC is developed in `Python <http://www.python.org/>`_ and requires at
least version 3.3. It only depends on
`asyncio <https://pypi.python.org/pypi/asyncio>`_ which is part of the
standard library since Python 3.4 anyway.

Features
--------

The main features are:

* Easy-to-use interface for IRC bots
* Internal event-loop that dispatches high-level IRC events
* Different kinds of tasks which can be scheduled by the user

.. note:: FredIRC is **already usable** but the project is still in an early
          stage of development. So far only the very basics needed to write
          simple IRC bots are implemented. As long as FredIRC has a 0.x.x
          version number, backward-incompatible API changes might be
          introduced (but mentioned in the change log).

For a more detailed list of features see the :doc:`history`.

Links
-----

* `Source Code Repository <https://github.com/worblehat/FredIRC>`_
* `PyPi-Site <https://pypi.python.org/pypi/FredIRC>`_
* `Issue Tracker <https://github.com/worblehat/FredIRC/issues>`_
* `Releases <https://github.com/worblehat/FredIRC/releases>`_

Documentation
-------------

.. toctree::
    :maxdepth: 1

    install
    guide
    api
    history

Development
-----------

FredIRC is **open source** and distributed under terms of the
`BSD 2-Clause license <http://opensource.org/licenses/BSD-2-Clause>`_.
Contributions (code, docs, ...) are always welcome!

Resources
+++++++++

* The source code repository is hosted at
  `Github <https://github.com/worblehat/FredIRC>`_
* See the :doc:`Changelog <history>` for the history of FredIRC
* For problems, questions and suggested improvements regarding FredIRC,
  please use the Github
  `issue tracker <https://github.com/worblehat/FredIRC/issues>`_ or
  contact me directly via tm[at]tobix[dot].eu
* Besides the :doc:`public API reference <api>` there is a reference that
  also includes the internal modules and classes not intended for use by the
  end user: :doc:`Internal API reference <api_internal>`

IRC Protocol
++++++++++++

FredIRC tries to implement RFC2812. But as this is no strict standard,
there might be problems with specific IRC Deamons. It was mostly tested with
ircd-hybrid.

Wishlist
++++++++

* Implement more handler methods for messages of the
  `IRC client protocol <http://tools.ietf.org/search/rfc2812>`_
* Allow multiple IRCClient instances and/or to re-run a terminated IRCClient
* Allow multiple server connections
* Utility classes for general bot development
* (X)DCC functionality
* Port to Python 3.0/3.1/3.2 (maybe by using
  `Trollius <http://trollius.readthedocs.org/>`_)
