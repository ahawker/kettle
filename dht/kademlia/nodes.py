import json
import math
import time
from kettle.dht.kademlia.client import Client
from kettle.dht.kademlia.server import Server
from kettle.dht.kademlia.identifier import unique_identifier

__author__ = 'ahawker'

class Node(object):
    def __init__(self, address='127.0.0.1', port=9090, id=None):
        self.address = address
        self.port = port
        self.id = id if id is not None else unique_identifier() #0 is valid

    def __repr__(self):
        return '<Node: ({0}:{1}) {2}>'.format(self.address, self.port, self.id)

    def __str__(self):
        return '{0}:{1}'.format(self.address, self.port)

    def __lt__(self, other):
        if isinstance(other, Node):
            return self.id < other.id
        return self.id < other

    def __le__(self, other):
        if isinstance(other, Node):
            return self.id <= other.id
        return self.id <= other

    def __gt__(self, other):
        if isinstance(other, Node):
            return self.id > other.id
        return self.id > other

    def __ge__(self, other):
        if isinstance(other, Node):
            return self.id >= other.id
        return self.id >= other

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return self.id == other

    def __ne__(self, other):
        if isinstance(other, Node):
            return self.id != other.id
        return self.id != other

    def __cmp__(self, other):
        if isinstance(other, Node):
            return cmp(self.id, other.id)
        return cmp(self.id, other)

    def __xor__(self, other):
        if isinstance(other, Node):
            return self.id ^ other.id
        return self.id ^ other

    def __hash__(self):
        return self.id

    def distance(self, other):
        return self ^ other

    def get_distance_bit(self, other):
        distance = self.distance(other)
        if distance < 0:
            raise ValueError('Node distance must be non-negative.')
        if not distance:
            return None
        return int(math.log(distance, 2))

    def to_dict(self):
        return { 'id' : self.id, 'address' : self.address, 'port' : self.port }

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_tuple(self):
        return self.address, self.port, self.id


class LocalNode(Node, Client, Server):
    def __init__(self, *args, **kwargs):
        super(LocalNode, self).__init__(*args, **kwargs)

class RemoteNode(Node):
    def __init__(self, *args, **kwargs):
        super(RemoteNode, self).__init__(*args, **kwargs)
        self.last_seen = time.time()
        self.failures = 0

    def is_responsive(self):
        return self.failures <= 5