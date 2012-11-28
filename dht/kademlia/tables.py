__author__ = 'ahawker'

from kettle.dht.kademlia.kbucket import KBucket

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

