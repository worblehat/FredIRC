# Copyright (c) 2013 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD  license.

""" This module provides a task class that can be used to schedule a function that will be executed by the event loop.

.. note:: A task will be scheduled only if there is a running(!) :py:class:`.IRCClient` instance in the same process.

There are two ways to use a Task:

1. Subclass Task and overwrite its run() method.
2. Instantiate the task directly and provide a function as parameter to the constructor.

"""

import asyncio
import types


class Task(object):
    """A Task represents a function that is executed at a specific time.

    After initialization the Task must be started explicitly via :py:meth:`.start()`.

    Args:
        delay (float): Time (in s) to defer the execution of the task after it is started or
                      the interval for it's repeated execution if ''repeat=True''.
        repeat (bool): If ''True'', the task will run periodically until it is stopped.
        func (function type): function that will be called (the actual task)
    """

    def __init__(self, delay, repeat=False, func=None):
        self._repeat = repeat
        self._delay = delay
        self._loop = asyncio.get_event_loop()
        self._handler = None
        if func:
            if isinstance(func, types.FunctionType):
                self.run = func
            else:
                raise TypeError('func is not a function type.')

    def run(self):
        """ Method that is called on execution of the Task.

        Can be overwritten in subclasses or by passing a function argument to the constructor.
        """
        pass

    def _run(self):
        self.run()
        if self._repeat:
            self.start()

    def start(self):
        """ Start the task.

        It will be executed in *delay* seconds.
        A started task can be stopped by calling :py:meth:`.stop()`.
        """
        if self._handler:
            self._handler.cancel()
        self._handler = self._loop.call_later(self._delay, self._run)

    def stop(self):
        """ Stop the task.

        Will have no effect if task is not running. The task might be started again later.
        """
        if self._handler:
            self._handler.cancel()
