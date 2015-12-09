#! /usr/bin/env python
#
# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD  license.


import sys

if sys.version < '3.3':
    print('ERROR: At least python version 3.3 is required!')
    sys.exit(1)

import os
from setuptools import setup

if sys.version_info[0:2] == (3,3):
    dependencies = ['asyncio']
else:
    dependencies = []

def read(file):
    """ Utility function to read the README-file. """
    return open(os.path.join(os.path.dirname(__file__), file)).read()

setup(
    name='FredIRC',
    version='0.3.0',
    author='Tobias Marquardt',
    author_email='tm@tobix.eu',
    description=('An easy-to-use, event driven framework for IRC bots.'),
    packages=['fredirc'],
    install_requires=dependencies,
    license='BSD',
    keywords='irc client library bot framework',
    url='https://worblehat.github.io/FredIRC',
    download_url='https://github.com/worblehat/FredIRC/archive/v0.3.0.tar.gz',
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    )

