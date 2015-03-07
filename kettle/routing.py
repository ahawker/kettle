"""
    kettle.routing
    ~~~~~~~~~~~~~~

    Contains functionality for dealing with tracking nodes within the network.
"""
__all__ = ['KBucket', 'RoutingTable']


import itertools

from kettle.constants import K, HASH_LENGTH


class KBucket:
    """
    Represents a bucket (and cache) for a nodes with a distance of 2^i to 2^i+1. Buckets store node
    contact information with least-recently seen at the head and most-recently seen at the tail.
    """
    def __init__(self, i, k=None):
        self.i = i
        self.k = k or K
        self.bucket = []
        self.cache = []

    def __repr__(self):
        return '<KBucket(i={0}, k={1}, bucket=({2},{1}), cache=({3},{1}))>'.format(self.k, len(self.bucket),
                                                                                   len(self.cache))

    def __str__(self):
        return 'KBucket({0}) ({2}/{1}) ({3}/{1})'.format(self.i, self.k, len(self.bucket), len(self.cache))

    def __contains__(self, item):
        return item in self.bucket or item in self.cache

    def __len__(self):
        return len(self.bucket) + len(self.cache)

    def ordered(self):
        return iter(reversed(self.bucket))

    def is_bucket_full(self):
        return len(self.bucket) >= self.k

    def is_bucket_empty(self):
        return len(self.bucket) <= 0

    def is_cache_full(self):
        return len(self.cache) >= self.k

    def is_cache_empty(self):
        return len(self.cache) <= 0

    def update(self, node):
        """
        Update the k-bucket with the given node.
        """
        if node in self:
            self.remove(node, False)
        if self.is_bucket_full():
            if not self.is_cache_full():
                self.cache.append(node)
        else:
            self.bucket.append(node)

    def remove(self, node, replace=True):
        """
        Remove a node from the k-bucket.
        """
        if node in self.bucket:
            self.bucket.remove(node)
            if replace and not self.is_cache_empty():
                self.bucket.append(self.cache.pop())
        elif node in self.cache:
            self.cache.remove(node)


class RoutingTable(object):
    """
    Represents a table that maintains nodes within a network across the entire id hash key space.
    """
    def __init__(self, node, k=None, sz=None):
        self.node_id = node.node_id
        self.k = k or K
        self.table = [KBucket(i + 1, k) for i in range(0, sz or HASH_LENGTH)]

    def __repr__(self):
        return '<{}(node_id={}, k={})>'.format(self.__class__.__name__, self.node_id, self.k)

    def __str__(self):
        return '{} [{}] {}/{}'.format(self.__class__.__name__, self.node_id.id, len(self), len(self.table) * self.k)

    def __len__(self):
        return sum(map(len, self.table))

    def __iter__(self):
        return iter(self.table)

    def update(self, node_id):
        """
        Update the network with the given node id.
        """
        if self.node_id == node_id:
            return

        index = self.node_id.get_distance_bit(node_id)
        self.table[index].update(node_id)

    def remove(self, node_id):
        """
        Remove the given node id from the network.
        """
        if self.node_id == node_id:
            return

        index = self.node_id.get_distance_bit(node_id)
        self.table[index].remove(node_id)

    def find_k_closest_nodes_triples(self, key, exclude=None, k=None):
        """
        Find the `k` closest nodes as a set of tuples.
        """
        return list(n.to_triple() for n in self.find_k_closest_nodes(key, exclude, k))

    def find_k_closest_nodes(self, key, exclude=None, k=None):
        """
        Find the `k` closest nodes.
        """
        return itertools.islice(self.find_closest_nodes(key, exclude), k or self.k)

    def find_closest_nodes(self, key, exclude=None):
        """
        Yields the `k` closest nodes.
        """
        for bucket in self.find_closest_buckets(key):
            for node_id in bucket.ordered():
                if node_id == exclude:
                    continue

                yield node_id

    def find_closest_buckets(self, key, start=0, end=160):
        """
        Yields the `k` closest buckets.

        To find the `k` closest buckets, we must start at the distance bit within the table
        and progressively step +-1 buckets away from the starting bit until we've exhausted all buckets.
        Once we reach the min/max of the hash key space, a None value will be yielded to denote no more buckets
        in that direction.
        """
        # Find the starting point (index of first k-bucket) to scan.
        index = self.node_id.get_distance_bit(key)

        # Go through +-1 bucket indicies and yield back buckets until we've exhausted the key space.
        for buckets in itertools.zip_longest(range(index, start - 1, -1), range(index + 1, end, 1)):
            yield from (self.table[b] for b in buckets if b is not None)
