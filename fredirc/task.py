# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

""" This module provides a task class. """

__all__ = ['Task']

import asyncio
import types


class Task(object):
    """A Task can be used to schedule a function that will be executed by the
    event loop.

    There are two ways to use a Task:

    1. Subclass Task and overwrite its :py:meth:`run()<.Task.run>` method.
    2. Instantiate the task directly and provide a function as parameter to the
       constructor.

    After initialization the Task must be started explicitly via
    :py:meth:`.start()`.

    Args:
        client (IRCClient): The :py:class:`IRCClient<.IRCClient>`-instance this
                            Task belongs to. The Task will not be able to run
                            unless the client is running.
        delay (float): Time (in seconds) to defer the execution of the task
                       after it was started or the interval for its repeated
                       execution if ``repeat=True``.
        repeat (bool): If ``True`` the task will run periodically until it is
                       stopped.
        func (function type): function that will be called (the actual task)
    """

    def __init__(self, client, delay, repeat=False, func=None):
        self._client = client
        self._delay = delay
        self._repeat = repeat
        self._handler = None
        if func:
            if isinstance(func, types.FunctionType):
                self.run = func
            else:
                raise TypeError('func is not a function type.')

    def run(self):
        """ Method that is called on execution of the Task.

        Can be overwritten in subclasses or by passing a function to
        the constructor.
        """
        pass

    def _run(self):
        self.run()
        if self._repeat:
            self.start()

    def start(self):
        """ Start the task.

        It will be executed in ``delay`` seconds (as specified in the constructor).
        A started task can be stopped by calling :py:meth:`.stop()`.
        """
        if self._handler:
            self._handler.cancel()
        if self._client.event_loop:
            self._handler = \
                self._client.event_loop.call_later(self._delay, self._run)

    def stop(self):
        """ Stop the task.

        Will have no effect if task is not running. The task might be started
        again later.
        """
        if self._handler:
            self._handler.cancel()
