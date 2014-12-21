Installation
============

**Prerequisites**: Make sure you have **Python 3.3 or above** as well as
`pip <https://pip.pypa.io>`_ installed on your system.

Installation via PyPI
----------------------

The **recommended way** to install FredIRC is to use the
`Python Package Index <https://pypi.python.org>`_.

The following command will download FredIRC (and dependencies) from
PyPI and install it for you:

.. code-block:: bash

    $ pip install fredirc

This is probably all you need to do. Now you can continue with the :doc:`guide`.

Installation from Source
------------------------

If you have FredIRC's source distribution (e.g. by cloning the
`git repository <https://github.com/worblehat/FredIRC>`_) and want to install
that version you need to create a distribution tarball first:

.. code-block:: bash

    $ python setup.py sdist

This will create a ``dist/``-directory with a gzip compressed tar archive, that
can be installed by:

.. code-block:: bash

    $ pip install dist/FredIRC-X.X.X.tar.gz

Build the Documentation
-------------------

The source tree of FredIRC also includes this documentation.
To build it, you will need to have
`sphinx <https://pypi.python.org/pypi/Sphinx>`_ and
`sphinxcontrib-napoleon <https://pypi.python.org/pypi/sphinxcontrib-napoleon>`_
installed.

.. code-block:: bash

    $ python setup.py build_sphinx


Afterwards you can open ``doc/build/html/index.html`` in your web browser.

Uninstall
---------

pip can also be used to uninstall FredIRC:

.. code-block:: bash

    $ pip uninstall fredirc

