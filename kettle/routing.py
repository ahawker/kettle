"""
    kettle.routing
    ~~~~~~~~~~~~~~

    Contains functionality for dealing with tracking nodes within the network.
"""
__all__ = ['KBucket', 'RoutingTable']


import itertools

from kettle.constants import K, HASH_LENGTH
from kettle.log import LOGGER


class KBucket:
    """
    Represents a bucket (and cache) for a nodes with a distance of 2^i to 2^i+1. Buckets store node
    contact information with least-recently seen at the head and most-recently seen at the tail.
    """
    def __init__(self, i, k=K):
        self.i = i
        self.k = k
        self.bucket = []
        self.cache = []
        self.logger = LOGGER.child(self)

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
        """
        Return iterable that yields back bucket nodes in most-recently seen order.
        """
        return iter(reversed(self.bucket))

    def is_bucket_full(self):
        """
        Return `True` if the node bucket is full.
        """
        return len(self.bucket) >= self.k

    def is_bucket_empty(self):
        """
        Return `True` if the node bucket is empty.
        """
        return len(self.bucket) <= 0

    def is_cache_full(self):
        """
        Return `True` if the node cache is full.
        """
        return len(self.cache) >= self.k

    def is_cache_empty(self):
        """
        Return `True` if the node cache is empty.
        """
        return len(self.cache) <= 0

    def update(self, node):
        """
        Update the k-bucket with the given node.

        :param node: Node to update in bucket.
        """
        # If this node is already in our bucket and cache, remove it and re-add it so we maintain
        # the most-recently seen ordering of the bucket and cache.
        if node in self:
            self.logger.debug('Updating existing node {} in bucket {}'.format(node, self.i))
            self.remove(node, False)

        # If the bucket is full, try and add the node to the cache if it isn't also full.
        if self.is_bucket_full():
            if self.is_cache_full():
                self.logger.debug('Ignoring node {} because bucket/cache {} is full'.format(node, self.i))
            else:
                self.logger.debug('Adding node {} to cache {}'.format(node, self.i))
                self.cache.append(node)

        # Add this node to our bucket since we have space. This is because it's either a new node
        # or an existing one we just removed.
        else:
            self.logger.debug('Adding node {} to bucket {}'.format(node, self.i))
            self.bucket.append(node)

    def remove(self, node, replace=True):
        """
        Remove a node from the k-bucket.

        :param node: Node in the bucket to remove.
        :param replace: Toggle if we should replace removed node with one from the cache; default: True.
        """
        # Remove node if exists in our main bucket.
        if node in self.bucket:
            self.logger.debug('Removing node {} from bucket {}'.format(node, self.i))
            self.bucket.remove(node)

            # If we're requesting a replacement and have active nodes in our cache,
            # replace the removed node with the most-recently seen node from the cache.
            if replace and not self.is_cache_empty():
                cached_node = self.cache.pop()
                self.logger.debug('Replacing with node {} from cache {}'.format(cached_node, self.i))
                self.bucket.append(cached_node)

        # Remove node if in our cache.
        elif node in self.cache:
            self.logger.debug('Removing node {} from cache {}'.format(node, self.i))
            self.cache.remove(node)


class RoutingTable(object):
    """
    Represents a table that maintains nodes within a network across the entire id hash key space.
    """
    def __init__(self, node, k=K, sz=HASH_LENGTH):
        self.node_id = node.node_id
        self.k = k
        self.sz = sz
        self.table = [KBucket(i, k) for i in range(0, self.sz)]
        self.logger = LOGGER.child(self)

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
        Update the table with the given node id.

        :param node_id: :class:`~kettle.id.NodeId` instance that represents a node in the table.
        """
        if self.node_id == node_id:
            return

        # Calculate index of KBucket to store node in based on distance from ourselves.
        index = self.node_id.get_distance_bit(node_id)
        self.logger.debug('Updating node {} from bucket {}'.format(node_id, index))

        self.table[index].update(node_id)

    def remove(self, node_id):
        """
        Remove the given node id from the table.

        :param node_id: :class:`~kettle.id.NodeId` instance that represents a node in the table.

        """
        if self.node_id == node_id:
            return

        # Calculate index of KBucket to store node in based on distance from ourselves.
        index = self.node_id.get_distance_bit(node_id)
        self.logger.debug('Removing node {} from bucket {}'.format(node_id, index))

        self.table[index].remove(node_id)

    def find_k_closest_nodes_triples(self, key, exclude=None, k=None):
        """
        Find the `k` closest nodes as a list of `triples`.

        A `triple` is a three item tuple that contains (host, port, id) of a node.

        :param key: Key used to find close nodes
        :param exclude: Optional :class:`~ktc.id.NodeId` to exclude from being considered; Default: `None`
        :param k: Optional maximum number of nodes to find; Default: `None`
        """
        return list(n.to_triple() for n in self.find_k_closest_nodes(key, exclude, k))

    def find_k_closest_nodes(self, key, exclude=None, k=None):
        """
        Find the `k` closest nodes.

        :param key: Key used to find close nodes
        :param exclude: Optional :class:`~ktc.id.NodeId` to exclude from being considered; Default: `None`
        :param k: Optional maximum number of nodes to find; Default: `None`
        """
        return itertools.islice(self.find_closest_nodes(key, exclude), k or self.k)

    def find_closest_nodes(self, key, exclude=None):
        """
        Generator that yields the ordered nodes, starting with those closest to the provided key.

        :param key: Key used to find close nodes
        :param exclude: Optional :class:`~ktc.id.NodeId` to exclude from being considered; Default: `None`
        """
        for bucket in self.find_closest_buckets(key):
            for node_id in bucket.ordered():
                if node_id != exclude:
                    yield node_id

    def find_closest_buckets(self, key, start=0, end=160):
        """
        Generator that yields all :class:`~ktc.routing.KBucket` instances in this routing table,
        in increasing order of distance away from the index of the :class:`~ktc.routing.KBucket` that holds
        the provided key.

        To find the closest buckets, we must start at the distance bit within the table that holds the provided key
        and progressively step +-1 buckets away from the starting bucket index until we've exhausted all buckets.
        Once we reach the min/max of the hash key space, a `None` value will be yielded to denote no more buckets
        in that direction.

        :param key: Key used to find close nodes
        :param start: Minimum index in the :class:`~ktc.routing.RoutingTable` to consider
        :param end: Maximum index in the :class:`~ktc.routing.RoutingTable` to consider
        """
        # Find the starting point (index of first k-bucket) to scan.
        index = self.node_id.get_distance_bit(key)

        # Go through +-1 bucket indicies and yield back buckets until we've exhausted the key space.
        for buckets in itertools.zip_longest(range(index, start - 1, -1), range(index + 1, end, 1)):
            yield from (self.table[b] for b in buckets if b is not None)
