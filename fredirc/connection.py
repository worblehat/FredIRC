# Copyright (c) 2013 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD  license.

"""
TODO
"""

from abc import ABCMeta
from abc import abstractmethod
import asyncio
from asyncio import DefaultEventLoopPolicy
import codecs
import logging
from queue import Queue
from threading import Thread

from fredirc.errors import NotConnectedError
from fredirc.task import Task


class ConnectionEvent(object):
    CONNECTED = 1
    DATA_AVAILABLE = 2
    SHUTDOWN = 3


class Connection(asyncio.Protocol, metaclass=ABCMeta):
    """ Abstract base class for a connection to an IRC server.

    A Connection wraps a network connection to the server. It uses the asyncio module internally for
    asynchronous communication to the server. The Connection also has a client instance and is responsible
    for forwarding messages from the server to the client and vice versa. The communication with the client
    must be implemented in subclasses by overwriting the abstract methods.

    .. note:: Only start(), terminate() und send_message() should be called from outside of the class (from
        the client object)!
    """

    def __init__(self, client, server, port):
        asyncio.Protocol.__init__(self)
        self._logger = logging.getLogger('FredIRC')
        self._client = client
        self._server = server
        self._port = port
        # Register customized decoding error handler
        codecs.register_error('log_and_replace', self._decoding_error_handler)

    @abstractmethod
    def connection_shutdown(self):
        """ TODO """
        raise NotImplementedError()

    @abstractmethod
    def connection_initiation(self):
        """ TODO """
        raise NotImplementedError()

    @abstractmethod
    def message_dispatching(self, message):
        """ TODO """
        raise NotImplementedError()

    @abstractmethod
    def message_delivering(self, message):
        """ TODO """
        raise NotImplementedError()

    @abstractmethod
    def start(self):
        """ Establish the connection and run the network event loop.

            This method might be blocking or non-blocking depending on it's actual implementation.
            From outside of the class, this is the method that should be called, *not* run()!
            Implementation notes:
            run() should be called from the implementation of start(). So this interface is compatible
            to Python's Thread module.
        """
        raise NotImplementedError()

    @abstractmethod
    def terminate(self):
        """ Gracefully terminate the Connection and the IO event loop.

        The client is notified that the connection is terminated and can no longer
        be used (by calling _signal_shutdown())..
        Any upcoming calls to send_message() will raise an exception.

        If the connection was not yet started or already terminated this method will have no effect and
        silently return.
        """
        raise NotImplementedError()

    def run(self):
        """ Runs the infinite event loop of the Connection.

            Blocks, until the event loop is terminated by calling terminate().
            This method intentionally fullfills the Thread interface, so a subclass of Connection that
            also inherits from Thread can be run in a separate thread without any modification to the event
            loop related code.
        """
        try:
            loop = asyncio.get_event_loop()
        except AssertionError:
            # No event loop in the current context (probably because we are not in the main thread).
            # Create an event loop from the default policy
            policy = DefaultEventLoopPolicy()
            policy.set_event_loop(policy.new_event_loop())
            asyncio.set_event_loop_policy(policy)
            loop = asyncio.get_event_loop()
        if not loop.is_running():
            task = asyncio.Task(loop.create_connection(self, self._server, self._port))
            loop.run_until_complete(task)
            loop.run_forever()

    def send_message(self, message):
        """ Send a message to the server.

        Args:
            message (str): A valid IRC message. Only carriage return and line feed are appended automatically.
        """
        self._logger.debug('Sending message: ' + message)
        message = message + '\r\n'
        self.message_delivering(message.encode('utf-8'))
        #TODO!!!    raise NotConnectedError("TODO")

    def data_received(self, data):
        """ Implementation of inherited method (from :class:`asyncio.Protocol`). """
        try:
            data = data.decode('utf-8', 'log_and_replace').splitlines()
            for message in data:
                self._logger.debug('Incoming message: ' + message)
                self.message_dispatching(message)
        # Shutdown client if unhandled exception occurs, as EventLoop does not provide a handle_error() method so far.
        except Exception:
            self._logger.exception('Unhandled Exception while running an IRCClient:')
            self._logger.critical('Shutting down the client, due to an unhandled exception!')
            self.terminate()


    def _decoding_error_handler(self, error):
        """ Error handler that is used with the byte.decode() method.

        Does the same as the built-in 'replace' error handler, but logs an error message before.

        Args:
            error (UnicodeDecodeError): The error that was raised during decode.
        """
        self._logger.error('Invalid character encoding: ' + error.reason)
        self._logger.error('Replacing the malformed character.')
        return codecs.replace_errors(error)


    def __call__(self):
        """ Returns this Connection instance. Used as factory method for BaseEventLoop.create_connection(). """
        return self

    # --- Implemented methods from asyncio.Protocol ---

    def connection_made(self, transport):
        """ Implementation of inherited method (from :class:`asyncio.Protocol`). """
        self._transport = transport
        self.connection_initiation()

    def connect_lost(self, exc):
        """ Implementation of inherited method (from :class:`asyncio.Protocol`). """
        self._logger.info('Connection closed.')
        self.terminate()

    def eof_received(self):
        """ Implementation of inherited method (from :class:`asyncio.Protocol`). """
        self._logger.debug('Received EOF')
        self.terminate()


class StandaloneConnection(Connection):

    def __init__(self, client, server, port):
        super().__init__(client, server, port)

    # --- Implemented methods superclasses ---

    def connection_initiation(self):
        self._client._connection_established()

    def connection_shutdown(self):
        self._client._connection_shutdown()

    def message_dispatching(self, message):
        self._client._handle(message)

    def message_delivering(self, message):
        self._transport.write(message)

    def start(self):
        """ TODO doc: imitates behaviour of Thread """
        self.run()

    def terminate(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop() #TODO really thread-safe?
            # TODO where to call close() on the loop?
            self.connection_shutdown()


class ThreadedConnection(Thread, Connection):

    def __init__(self, client, server, port):
        Thread.__init__(self)
        Connection.__init__(self, client, server, port)
        # Queues for synchronized communication with IRCClient
        self._in_queue = Queue()    # Connection -> IRCCLient
        self._out_queue = Queue()   # IRCCLient -> Connection
        self._out_task = None

    def has_in_event(self):
        return self._in_queue.qsize() > 0

    def has_out_event(self):
        return self._out_queue.qsize() > 0

    def process_next_in_event(self):
        """
        TODO document: pass silently when no event
        """
        event, data = self._in_queue.get()
        if event == ConnectionEvent.CONNECTED:
            # TODO assert: not connected yet
            self._logger.info('Connected to server.')
            self._client._connection_established()
        elif event == ConnectionEvent.SHUTDOWN:
            self._client._connection_shutdown()
        elif event == ConnectionEvent.DATA_AVAILABLE:
            self._client._handle(data)

    # --- Implemented methods superclasses ---

    #TODO why do we need to explicitly override this?!
    def run(self):
        Connection.run(self)

    def start(self):
        Thread.start(self)

    def message_dispatching(self, message):
        self._in_queue.put((ConnectionEvent.DATA_AVAILABLE, message))

    def message_delivering(self, message):
        self._out_queue.put((ConnectionEvent.DATA_AVAILABLE, message))

    def connection_initiation(self):
        self._in_queue.put((ConnectionEvent.CONNECTED, None))
        if not self._out_task:

            def process_out_events():
                while self.has_out_event():
                    event, data = self._out_queue.get()
                    if event == ConnectionEvent.DATA_AVAILABLE:
                        self._transport.write(data)
                    elif event == ConnectionEvent.SHUTDOWN:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            loop.stop() #TODO really thread-safe?
                            # TODO where to call close() on the loop?
                            self.connection_shutdown()

            self._out_task = Task(0.1, True, process_out_events)
            self._out_task.start()

    def connection_shutdown(self):
        self._in_queue.put((ConnectionEvent.SHUTDOWN, None))

    def terminate(self):
        self._out_queue.put((ConnectionEvent.SHUTDOWN, None))
