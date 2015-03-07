"""
    kettle.protocol
    ~~~~~~~~~~~~~~~

    Contains the Kademlia DHT protocol.
"""
__all__ = ['Protocol', 'ClientProtocol', 'ServerProtocol', 'rpc']


import asyncio
import functools

from kettle.codec import CodecError, JSONCodec
from kettle.constants import DEFAULT_REQUEST_TIMEOUT
from kettle.exceptions import KettleRpcTimeout
from kettle.id import Id
from kettle.message import Message, KettleMessageFormatError, MessageType


def rpc(func):
    """
    Decorator to define a RPC (remote procedure call) to other nodes in the network.
    """
    @asyncio.coroutine
    @functools.wraps(func)
    def local(self, address, *args, timeout=None):
        """
        Local @rpc handler for sending RPC request to a remote node.
        """
        # Build and send request for rpc call to a remote node.
        msg = Message.request(self.id, self.address, func.__name__, args)

        # Wait for future to return result of rpc call on remote node.
        response = yield from self.connection.send_request(msg, address, timeout=timeout)

        # Update routing table with id/address of remote node.
        node_id = Id(response.address, response.node_id)
        self.table.update(node_id)

        return response.payload

    @asyncio.coroutine
    @functools.wraps(func)
    def remote(self, msg, address):
        """
        Remote @rpc handler for receiving RPC request and returning response to caller.
        """
        # Create identifier for request node.
        node_id = Id(msg.address, msg.node_id)
        try:
            # Call decorated func to generate rpc payload result.
            result = func(self, node_id, *msg.payload)

            # Build and send response message containing result.
            response = Message.response(self.id, self.address, msg.rpc, msg.rpc_id, result)
            self.connection.send_response(response, address)
        finally:
            # Update routing table with latest info from request node.
            self.table.update(node_id)

    local.__remote__ = remote
    return local


def msg(message_type):
    """
    Decorator that defines callback handlers based on the incoming message type.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.__handler__ = message_type
        return wrapper
    return decorator


def get_handlers(protocol):
    """
    Get mapping of all incoming message request handlers for a protocol instance.
    """
    return dict(((h.__handler__.name, h)
                 for h in (getattr(protocol, a)
                           for a in dir(protocol)) if hasattr(h, '__handler__')))


def get_remotes(endpoint):
    """
    Get mapping of all @rpc decorated functions on an endpoint that are exposed.
    """
    return dict(((h.__remote__.__name__, h.__remote__)
                 for h in (getattr(endpoint, a)
                           for a in dir(endpoint)) if hasattr(h, '__remote__')))


class Protocol(asyncio.DatagramProtocol):
    """
    Protocol for sending/receiving requests to other nodes in a Kademlia DHT network.
    """

    #:
    codec_factory = JSONCodec

    #:
    message_factory = Message

    #:
    default_request_timeout = DEFAULT_REQUEST_TIMEOUT

    #:
    default_request_timeout_exception = KettleRpcTimeout

    #:
    inbound_message_factory = None

    #:
    outbound_message_factory = None

    def __init__(self, endpoint=None, loop=None):
        self.endpoint = endpoint
        self.loop = loop
        self.codec = self.codec_factory()
        self.transport = None
        self.error_count = 0
        self.futures = {}
        self.remotes = get_remotes(endpoint)
        self.handlers = get_handlers(self)

    def connection_made(self, transport):
        """
        Callback raised by asyncio protocol when connected.
        """
        self.transport = transport
        self.loop.create_task(self.on_connect(transport))

    def connection_lost(self, exc):
        """
        Callback raised by asyncio protocol when disconnected.
        """
        self.transport = None
        self.error_count = 0
        self.loop.create_task(self.on_disconnect(exc))

    def datagram_received(self, data, address):
        """
        Callback raised by asyncio protocol when UDP datagram is received.
        """
        try:
            data = self.codec.decode(data)
        except CodecError as e:
            self.endpoint.logger.warning('Invalid incoming data encoding: {} from {}:{}'.format(e, *address))
        else:
            try:
                message = self.message_factory.from_dict(data)
            except KettleMessageFormatError as e:
                self.endpoint.logger.warning('Invalid incoming message: {} from {}:{}'.format(e, *address))
            else:
                self.loop.create_task(self.on_message(message, address))

    def error_received(self, exc):
        """
        Callback raised by asyncio protocol when datagram received causes an error.
        """
        self.error_count += 1
        self.loop.create_task(self.on_error(exc))

    def send_message(self, msg, address):
        """
        Send an arbitrary message object to the given address.
        """
        if self.transport:
            try:
                msg = self.message_factory.to_dict(msg)
            except KettleMessageFormatError as e:
                self.endpoint.logger.warning('Invalid outgoing message data: {} to {}:{}'.format(e, *address))
            else:
                try:
                    data = self.codec.encode(msg)
                except CodecError as e:
                    self.endpoint.logger.warning('Invalid outgoing data encoding: {} to {}:{}'.format(e, *address))
                else:
                    self.transport.sendto(data, address)

    def send_request(self, request, address, timeout=None, exception=None):
        """
        Send an RPC request to the given node address.
        """
        # Build future to track this RPC request.
        timeout = timeout or self.default_request_timeout
        future = self.futures[request.rpc_id] = asyncio.Future(loop=self.loop)

        # Register callback to handle request timeouts.
        self.loop.call_later(timeout, self.on_send_request_timeout, request.rpc_id, exception)

        # Send request to remote node.
        self.send_message(request, address)
        return future

    def send_response(self, response, address):
        """
        Send an RPC response to the given node address.
        """
        return self.send_message(response, address)

    def on_send_request_timeout(self, request_id, exception=None):
        """
        Callback raised when RPC request future reaches its send timeout. If the future is still outstanding,
        it means that no response has been received and we should raise some sort of notification to the caller.
        """
        future = self.futures.pop(request_id, None)
        if future:
            future.set_exception(exception or self.default_request_timeout_exception)

    def close(self):
        """
        Close the protocol.
        """
        if self.transport:
            self.transport.close()

    @asyncio.coroutine
    def on_connect(self, transport):
        """
        Callback raised by protocol when connected.
        """
        name = transport.get_extra_info('sockname')
        self.endpoint.logger.info('Connected to transport {}:{}'.format(*name))

    @asyncio.coroutine
    def on_disconnect(self, exc):
        """
        Callback raised by protocol when disconnected.
        """
        self.endpoint.logger.info('Disconnected from transport')

    @asyncio.coroutine
    def on_error(self, exc):
        """
        Callback raised by error when error received.
        """
        self.endpoint.logger.warning('Previous message could not be delivered! {}'.format(exc))

    @asyncio.coroutine
    def on_message(self, msg, address):
        """
        Callback raised when a valid message is received.
        """
        try:
            handler = self.handlers[msg.type]
        except KeyError:
            self.endpoint.logger.warning('Invalid incoming message type: {} from {}:{}'.format(msg.type, *address))
        else:
            yield from handler(msg, address)


    @msg(MessageType.request)
    @asyncio.coroutine
    def on_message_request(self, message, address):
        """
        Callback raised when a valid request message is received.
        """
        try:
            remote = self.remotes[message.rpc]
        except KeyError:
            self.endpoint.logger.warning('Invalid request rpc type: {} from {}:{}'.format(message.func, *address))
        else:
            yield from remote(self.endpoint, message, address)

    @msg(MessageType.response)
    @asyncio.coroutine
    def on_message_response(self, message, address):
        """
        Callback raised when a valid response message is received.
        """
        try:
            future = self.futures[message.rpc_id]
        except KeyError:
            self.endpoint.logger.warning('Invalid response message id: {} from {}:{}'.format(message.rpc_id, *address))
        else:
            if not future.cancelled():
                future.set_result(message)


class ServerProtocol(Protocol):
    """
    """


class ClientProtocol(Protocol):
    """
    """

