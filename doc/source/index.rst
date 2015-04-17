
.. include:: ../../README.rst

Documentation
-------------

.. toctree::
    :maxdepth: 1

    install
    guide
    api
    history

Contact
-------

Please use the `issue tracker <https://github.com/worblehat/FredIRC/issues>`_
or contact me via mail (tm[at]tobix[dot]eu).

Development
-----------

FredIRC is **open source** and distributed under terms of the
`2-clause BSD license <http://opensource.org/licenses/BSD-2-Clause>`_.
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
