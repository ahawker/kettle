__author__ = 'ahawker'

import hashlib
import json
import random
import time

class Node(object):
    def __init__(self, address, port, nid=None):
        self.address = address
        self.port = port
        if nid is None:
            nid = hashlib.sha1(str(random.getrandbits(160))).digest()
        self.nid = nid

    def __repr__(self):
        return '<Node ({0}:{1}) {2}>'.format(self.address, self.port, self.nid)

    def __str__(self):
        return '{0}:{1}'.format(self.address, self.port)

    def __lt__(self, other):
        if isinstance(other, Node):
            return self.nid < other.nid
        return self.nid < other

    def __le__(self, other):
        if isinstance(other, Node):
            return self.nid <= other.nid
        return self.nid <= other

    def __gt__(self, other):
        if isinstance(other, Node):
            return self.nid > other.nid
        return self.nid > other

    def __ge__(self, other):
        if isinstance(other, Node):
            return self.nid >= other.nid
        return self.nid >= other

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.nid == other.nid
        return self.nid == other

    def __ne__(self, other):
        if isinstance(other, Node):
            return self.nid != other.nid
        return self.nid != other

    def __cmp__(self, other):
        if isinstance(other, Node):
            return cmp(self.nid, other.nid)
        return cmp(self.nid, other)

    def __xor__(self, other):
        if isinstance(other, Node):
            return self.nid ^ other.nid
        return self.nid ^ other

    def __hash__(self):
        return self.nid

    def distance(self, other):
        return self ^ other

    def to_dict(self):
        return { 'id' : self.nid, 'address' : self.address, 'port' : self.port }

    def to_json(self):
        return json.dumps(self.to_dict())


class LocalNode(Node):
    def __init__(self, *args, **kwargs):
        super(LocalNode, self).__init__(*args, **kwargs)


class RemoteNode(Node):
    def __init__(self, *args, **kwargs):
        super(RemoteNode, self).__init__(*args, **kwargs)
        self.last_seen = time.time()



