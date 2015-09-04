"""
    kettle.connection
    ~~~~~~~~~~~~~~~~~

    Contains functionality for specifying specific connection types to a DHT.
"""
__all__ = ['Connection', 'ClientConnection', 'ServerConnection', 'Endpoint']


import asyncio

from kettle.log import LOGGER
from kettle.protocol import ClientProtocol, ServerProtocol


class Connection:
    """
    Base class describing a specific connection to a DHT network.
    """

    protocol_factory = None

    def __init__(self, address, loop):
        self.address = address
        self.loop = loop
        self.protocol = None
        self.logger = LOGGER.child(self)

    def __repr__(self):
        return '<{}(address={}, protocol={})>'.format(self.__class__.__name__, self.address,
                                                      self.protocol_factory.__name__)

    @asyncio.coroutine
    def connect(self, endpoint):
        """
        Create protocol and connect to endpoint defined by connection type.
        """
        self.protocol = self.protocol_factory(endpoint=endpoint, loop=self.loop)
        yield from self.create_endpoint(lambda: self.protocol, self.address)

    @asyncio.coroutine
    def create_endpoint(self, protocol_factory, address):
        """
        Abstract method to override with specific endpoint connection logic.
        """
        raise NotImplementedError('create_endpoint must be implemented in derived class!')

    def send_request(self, request, address, timeout=None):
        """
        Send a new request to the connection endpoint.
        """
        return self.protocol.send_request(request, address, timeout=timeout)

    def send_response(self, response, address):
        """
        Send a response message to the connection endpoint.
        """
        return self.protocol.send_response(response, address)

    def disconnect(self):
        """
        Close connection.
        """
        self.protocol.close()


class ClientConnection(Connection):
    """
    Connection type for actors that wish to query the DHT network without participating.
    """

    protocol_factory = ClientProtocol

    @asyncio.coroutine
    def create_endpoint(self, protocol_factory, address):
        yield from self.loop.create_datagram_endpoint(protocol_factory, remote_addr=address)


class ServerConnection(Connection):
    """
    Connection type for actors that wish to listen for incoming DHT network queries.
    """

    protocol_factory = ServerProtocol

    @asyncio.coroutine
    def create_endpoint(self, protocol_factory, address):
        yield from self.loop.create_datagram_endpoint(protocol_factory, local_addr=address)


class Endpoint:
    """
    Represents either a client or server within the network.
    """

    connection_factory = None

    def __init__(self, address, loop=None):
        self.connection = self.connection_factory(address, loop)
        self.loop = loop
        self.logger = LOGGER.child(self)

    def __repr__(self):
        return '<{}(connection={})>'.format(self.__class__.__name__, self.connection)

    @property
    def address(self):
        return self.connection.address

    def connect(self):
        connector = self.connection.connect(self)
        return self.loop.run_until_complete(connector)

    def disconnect(self):
        return self.connection.disconnect()
