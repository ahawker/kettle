"""
    kettle.id
    ~~~~~~~~~

    Contains implementation of identifiers used for tracking items and peers in a network.
"""
__all__ = ['Id', 'NodeId']


import hashlib
import random

from kettle.constants import HASH_LENGTH, ID_ENDIANNESS, ID_SIGNED


class Id:
    """
    Helper class for automatically generating identifiers used in the DHT.
    """

    @staticmethod
    def from_key(key, byteorder=ID_ENDIANNESS, signed=ID_SIGNED):
        """
        Generate new identifier from the provided key.

        :param key: Key used to generate identifier hash.
        :param byteorder: Endianness of the identifier; default: `sys.byteorder`
        :param signed: Boolean flag indicating if the identifier is signed or unsigned; default: `False`
        """
        key = key.encode() if hasattr(key, 'encode') else key
        key_as_bytes = hashlib.sha1(key).digest()
        return int.from_bytes(key_as_bytes, byteorder=byteorder, signed=signed)

    @classmethod
    def random(cls, sz=HASH_LENGTH, byteorder=ID_ENDIANNESS, signed=ID_SIGNED):
        """
        Generate a random identifier based on the given parameters.

        :param sz: Size of hash keyspace; default: `160`
        :param byteorder: Endianness of the identifier; default: `sys.byteorder`
        :param signed: Boolean flag indicating if the identifier is signed or unsigned; default: `False`
        """
        key = random.getrandbits(sz)
        key_as_bytes = key.to_bytes(sz // 8, byteorder=byteorder, signed=signed)
        return cls.from_key(key_as_bytes, byteorder, signed)


class NodeId:
    """
    Identifier that represents a node that is a member of the DH.
    """

    @classmethod
    def from_triple(cls, triple):
        """
        Create :class:`~kettle.id.NodeId` instance from a `triple`.

        A `triple` is a tuple containing three values: host, port, id.

        :param triple: Tuple containing three values (host, port, id).
        """
        return cls(triple[:2], triple[2])

    def __init__(self, address, id=None):
        self.address = address
        self.id = id or Id.random()

    def __repr__(self):
        return '<{}(address={}, id={}>'.format(self.__class__.__name__, self.address, self.id)

    def __str__(self):
        return str(self.id)

    def __lt__(self, other):
        if isinstance(other, NodeId):
            return self.id < other.id
        return self.id < other

    def __le__(self, other):
        if isinstance(other, NodeId):
            return self.id <= other.id
        return self.id <= other

    def __gt__(self, other):
        if isinstance(other, NodeId):
            return self.id > other.id
        return self.id > other

    def __ge__(self, other):
        if isinstance(other, NodeId):
            return self.id >= other.id
        return self.id >= other

    def __eq__(self, other):
        if isinstance(other, NodeId):
            return self.id == other.id
        return self.id == other

    def __ne__(self, other):
        if isinstance(other, NodeId):
            return self.id != other.id
        return self.id != other

    def __xor__(self, other):
        if isinstance(other, NodeId):
            return self.id ^ other.id
        return self.id ^ other

    def __hash__(self):
        return self.id

    def to_triple(self):
        """
        Return node identifier information in the form of a `triple`.

        A `triple` is a tuple containing three values: host, port, id.
        """
        return self.address[0], self.address[1], self.id

    def distance(self, other):
        """
        Get the distance between ourselves and another identifier.
        """
        return self ^ other

    def get_distance_bit(self, other):
        """
        Get the distance bit (most significant bit) between two nodes.

        This value will determine its placement in a :class:`~kettle.routing.KBucket`
        """
        distance = self.distance(other)
        bit = -1
        while distance:
            distance >>= 1
            bit += 1
        return max(0, bit)