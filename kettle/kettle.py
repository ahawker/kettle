__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'

import hashlib
import itertools
import json
import math
import random
import time

def uid():
    return int(hashlib.sha1(str(random.getrandbits(160))).hexdigest(), 16)

class KBucket(object):
    def __init__(self, k=20):
        super(KBucket, self).__init__()
        self.k = k
        self.bucket = []
        self.cache = []

    def __repr__(self):
        return '<KBucket: {0} {1} {2}>'.format(self.k, self.bucket, self.cache)

    def __str__(self):
        return 'KBucket[{0}] ({1}/{3}) ({2}/{3})'.format(len(self), len(self.bucket), len(self.cache), self.k)

    def __contains__(self, item):
        return item in self.bucket or item in self.cache

    def __len__(self):
        return len(self.bucket) + len(self.cache)

    def __iter__(self):
        return itertools.chain(self.bucket, self.cache)

    @property
    def is_bucket_full(self):
        return len(self.bucket) >= self.k

    @property
    def is_cache_full(self):
        return len(self.cache) >= self.k

    def add(self, node):
        if node in self:
            self.remove(node)
        if self.is_bucket_full:
            if self.is_cache_full:
                self.cache.pop()
            self.cache.append(node)
        else:
            self.bucket.append(node)

    def remove(self, node):
        if node in self.bucket:
            self.bucket.remove(node)
        elif node in self.cache:
            self.cache.remove(node)

class RoutingTable(object):
    def __init__(self, owner, k=20):
        self.owner = owner
        self.table = [KBucket(k) for _ in range(0, 160)]

    def __repr__(self):
        return '<RoutingTable: {0} {1}>'.format(self.owner, sum(map(len, self.table)))

    def __str__(self):
        return 'RoutingTable[{0}]'.format('\n'.join(map(str, self.table)))

    def __iter__(self):
        return iter(self.table)

    def add(self, node):
        if self.owner == node:
            return
        index = self.owner.get_distance_bit(node)
        self.table[index].add(node)

    def remove(self, node):
        if self.owner == node:
            return
        index = self.owner.get_distance_bit(node)
        self.table[index].remove(node)

class Node(object):
    def __init__(self, address='127.0.0.1', port=9090, id=uid()):
        self.address = address
        self.port = port
        self.id = id

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


class LocalNode(Node):
    def __init__(self, *args, **kwargs):
        super(LocalNode, self).__init__(*args, **kwargs)

class RemoteNode(Node):
    def __init__(self, *args, **kwargs):
        super(RemoteNode, self).__init__(*args, **kwargs)
        self.last_seen = time.time()
        self.failures = 0

    def is_responsive(self):
        return self.failures <= 5

class Client(object):
    pass

class Server(object):
    pass

