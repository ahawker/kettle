"""
    kettle.node
    ~~~~~~~~~~~

    ...
"""
__all__ = ['Server', 'Node']

import asyncio
import itertools

from kettle import get_event_loop
from kettle.connection import Endpoint, ServerConnection
from kettle.constants import ALPHA
from kettle.id import Id
from kettle.protocol import rpc
from kettle.routing import RoutingTable


class Server(Endpoint):
    """
    Represents a server within the network listening on a specific connection.
    """

    connection_factory = ServerConnection

    def listen(self):
        """
        Listen for incoming requests on the connection until explicitly stopped.
        """
        return self.connect()

    def run_forever(self):
        """
        """
        # Setup local socket listening connection.
        self.listen()

        # Listen on socket for incoming connections until explicitly stopped.
        try:
            self.logger.info('Listening on socket {}:{}'.format(*self.address))
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.logger.info('Shutting down')
            self.connection.disconnect()
            self.loop.close()


class Node(Server):
    """
    Represents a node within the network.

    Nodes are cooperative members of the network. They are responsible for listening to requests, storing data
    and fulfilling all the requirements of being a network peer.
    """

    def __init__(self, address, loop=None, alpha=None):
        super(Node, self).__init__(address, loop)
        self.node_id = Id(address)
        self.table = RoutingTable(self)
        self.db = dict()
        self.alpha = alpha or ALPHA

    @property
    def id(self):
        return self.node_id.id

    @property
    def address(self):
        return self.node_id.address

    @rpc
    def ping(self, node_id):
        """
        RPC handler to send/receive `ping` requests.

        Ping is used to determine if a node is online.
        """
        return self.id

    @rpc
    def store(self, node_id, key, value):
        """
        RPC handler to send/receive `store` requests.

        Store is used to instruct node to store key/value pair.
        """
        self.db[key] = value
        return True

    @rpc
    def find_node(self, node_id, key):
        """
        RPC handler to send/receive `find_node` requests.

        Find_node is used find a specific node within the network.
        """
        return self.table.find_k_closest_nodes_triples(key, exclude=node_id)

    @rpc
    def find_value(self, node_id, key):
        """
        RPC handler to send/receive `find_value` requests.

        Find_value is used to find a specific value within the network.
        """
        try:
            return True, self.db[key]
        except KeyError:
            return False, self.table.find_k_closest_nodes_triples(key, exclude=node_id)

    def lookup_node(self, key):
        """
        Perform a node lookup.
        """
        def is_completed(future, results):
            """
            """
            nodes = yield from future
            return nodes

        return self.lookup(key, self.find_node, is_completed)

    def lookup_value(self, key):
        """
        Perform a value lookup.
        """
        def is_completed(future, results):
            """
            """
            return (yield from future)

        return self.lookup(key, self.find_value, is_completed)

    def lookup(self, key, find, predicate):
        """
        Perform a node or value lookup in the network.

        TODO
        """
        # Grab alpha of our k-closest nodes. If we don't know of any nodes, fail immediately.
        closest = set(self.table.find_k_closest_nodes(key, k=self.alpha))
        if not closest:
            raise KeyError('Routing table is empty')

       # k_closest = set()
        queried = set()

        closest_node = None

        for i in itertools.count():

            remaining = closest - queried
            if not remaining:
                break

            alpha_closest = None

            for future in asyncio.as_completed((find(node, key) for node in alpha_closest), loop=self.loop):
                try:
                    completed, result = predicate(future, closest)
                except Exception:
                    pass
                else:
                    if completed:
                        return result

                    closest.add((Id.from_triple(n) for n in result))
        else:
            pass

            #for future in asyncio.as_completed(())

        # ...
        # take alpha from closest and make RPC calls to them
        # if we found the value, end quickly
        #
        #alpha_nodes = closest[:self.alpha]
        #futures = (func(n, key) for n in alpha_nodes)

            # result = yield from f
            # futures2 = [func(n, key) for n in result]
            # for f2 in asyncio.as_completed(futures2, loop=self.loop):
            #     pass

    def lookup2(self, key, func, nodes, visited, cb):
        """
        TODO
        """
        for future in asyncio.as_completed((func(node, key) for node in nodes), loop=self.loop):
            try:
                completed, result = cb(future)
                if completed:
                    return result
                return None
            except Exception:
                pass
            #yield from (yield from future)
            #return None
            #result = yield from future
            #yield result


    def lookup_nodes(self, key):
        """
        TODO
        """
        # function which takes a list of nodes and async find_node or find_value's them
        # if find_value and value found, done
        # otherwise continue on
        # if find_node, continue on


def main():

    loop = get_event_loop()
    node = Node(('127.0.0.1', 8888), loop=loop)
    node.listen()

    for i in range(0, 10):
        print(i)
        loop.run_until_complete(node.store(('127.0.0.1', 8889), 'key_{}'.format(i), i))
        loop.run_until_complete(node.ping(('127.0.0.1', 8889)))
        loop.run_until_complete(node.find_value(('127.0.0.1', 8889), Id.new_id()))


if __name__ == '__main__':
    main()

