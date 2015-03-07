"""
    kettle.id
    ~~~~~~~~~

    Contains implementation of identifiers used for tracking items and peers in a network.
"""
__all__ = ['Id']


import hashlib
import math
import random

from kettle.constants import HASH_LENGTH


class Id:
    """
    Represents identifier used for consistent hashing of items in a table.
    """

    @staticmethod
    def new_id(sz=HASH_LENGTH):
        return int(hashlib.sha1(str(random.getrandbits(sz)).encode()).hexdigest(), 16)

    @classmethod
    def from_triple(cls, triple):
        return cls(triple[:2], triple[2])

    def __init__(self, address, id=None):
        self.address = address
        self.id = id or self.new_id()

    def __repr__(self):
        return '<{}(address={}, id={}>'.format(self.__class__.__name__, self.address, self.id)

    def __lt__(self, other):
        if isinstance(other, Id):
            return self.id < other.id
        return self.id < other

    def __le__(self, other):
        if isinstance(other, Id):
            return self.id <= other.id
        return self.id <= other

    def __gt__(self, other):
        if isinstance(other, Id):
            return self.id > other.id
        return self.id > other

    def __ge__(self, other):
        if isinstance(other, Id):
            return self.id >= other.id
        return self.id >= other

    def __eq__(self, other):
        if isinstance(other, Id):
            return self.id == other.id
        return self.id == other

    def __ne__(self, other):
        if isinstance(other, Id):
            return self.id != other.id
        return self.id != other

    def __xor__(self, other):
        if isinstance(other, Id):
            return self.id ^ other.id
        return self.id ^ other

    def __hash__(self):
        return self.id

    def to_triple(self):
        return self.address[0], self.address[1], self.id

    def distance(self, other):
        return self ^ other

    def get_distance_bit(self, other):
        distance = self.distance(other)
        if distance < 0:
            raise ValueError('Node distance must be non-negative.')

        if not distance:
            return None

        # We only want the lowest bit set for distance.
        if (distance & (distance - 1)) != 0:
            distance &= ~ (distance - 1)

        return int(math.log(distance, 2))
