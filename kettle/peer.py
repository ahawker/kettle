"""
    kettle.peer
    ~~~~~~~~~~

    Contains implementation of a consumer of a DHT network.
"""
__all__ = ['Client']


from kettle import get_event_loop
from kettle.connection import Endpoint, ClientConnection
from kettle.node import Node


class Client(Endpoint):
    """

    """

    connection_factory = ClientConnection


def main():
    import logging

    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    loop = get_event_loop()
    node = Node(('127.0.0.1', 8889), loop=loop)
    node.run_forever()


if __name__ == '__main__':
    main()